const {onCall, onRequest, HttpsError} = require('firebase-functions/v2/https');
const {defineSecret} = require('firebase-functions/params');
const admin = require('firebase-admin');
const Stripe = require('stripe');

admin.initializeApp();
const db = admin.firestore();
const stripeKey = defineSecret('STRIPE_SECRET_KEY');
const webhookKey = defineSecret('STRIPE_WEBHOOK_SECRET');

function uidOf(request) {
  if (!request.auth) throw new HttpsError('unauthenticated', 'Нэвтэрнэ үү.');
  return request.auth.uid;
}
function id(value) {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(value)) {
    throw new HttpsError('invalid-argument', 'Буруу код.');
  }
  return value;
}

exports.startRental = onCall(async (request) => {
  const uid = uidOf(request);
  const bikeId = id(request.data.bikeId);
  const userRef = db.collection('users').doc(uid);
  const bikeRef = db.collection('bikes').doc(bikeId);
  const rentalRef = db.collection('rentals').doc();
  return db.runTransaction(async (tx) => {
    const [user, bike] = await Promise.all([tx.get(userRef), tx.get(bikeRef)]);
    if (!user.exists) throw new HttpsError('failed-precondition', 'Профайл үүсээгүй байна.');
    if (user.data().activeRentalId || user.data().unpaidRentalId) {
      throw new HttpsError('failed-precondition', 'Идэвхтэй эсвэл төлөөгүй түрээс байна.');
    }
    if (!bike.exists || bike.data().status !== 'available') {
      throw new HttpsError('failed-precondition', 'Дугуй сул биш байна.');
    }
    const stationId = bike.data().stationId;
    const stationRef = db.collection('stations').doc(stationId);
    const station = await tx.get(stationRef);
    if (!station.exists || station.data().availableCount < 1) {
      throw new HttpsError('failed-precondition', 'Зогсоолын мэдээлэл буруу байна.');
    }
    tx.update(bikeRef, {status: 'in_use', stationId: null});
    tx.update(stationRef, {availableCount: admin.firestore.FieldValue.increment(-1)});
    tx.update(userRef, {activeRentalId: rentalRef.id});
    tx.create(rentalRef, {userId: uid, bikeId, startStationId: stationId,
      startedAt: admin.firestore.FieldValue.serverTimestamp(), status: 'active'});
    return {rentalId: rentalRef.id};
  });
});

exports.finishRental = onCall(async (request) => {
  const uid = uidOf(request);
  const stationId = id(request.data.stationId);
  const userRef = db.collection('users').doc(uid);
  const stationRef = db.collection('stations').doc(stationId);
  return db.runTransaction(async (tx) => {
    const user = await tx.get(userRef);
    const rentalId = user.data()?.activeRentalId;
    if (!rentalId) throw new HttpsError('failed-precondition', 'Идэвхтэй түрээс алга.');
    const rentalRef = db.collection('rentals').doc(rentalId);
    const [rental, station] = await Promise.all([tx.get(rentalRef), tx.get(stationRef)]);
    if (!rental.exists || rental.data().userId !== uid || rental.data().status !== 'active') {
      throw new HttpsError('failed-precondition', 'Түрээсийн төлөв буруу байна.');
    }
    if (!station.exists || station.data().enabled !== true ||
        station.data().availableCount >= station.data().capacity) {
      throw new HttpsError('failed-precondition', 'Энэ зогсоолд буцаах боломжгүй.');
    }
    const bikeRef = db.collection('bikes').doc(rental.data().bikeId);
    const bike = await tx.get(bikeRef);
    if (!bike.exists || bike.data().status !== 'in_use') {
      throw new HttpsError('failed-precondition', 'Дугуйн төлөв буруу байна.');
    }
    const started = rental.data().startedAt?.toMillis();
    if (!started) throw new HttpsError('failed-precondition', 'Эхэлсэн цаг тодорхойгүй.');
    const minutes = Math.max(1, Math.ceil((Date.now() - started) / 60000));
    const cents = Math.max(50, minutes * 50);
    tx.update(bikeRef, {status: 'available', stationId});
    tx.update(stationRef, {availableCount: admin.firestore.FieldValue.increment(1)});
    tx.update(userRef, {activeRentalId: admin.firestore.FieldValue.delete(), unpaidRentalId: rentalId});
    tx.update(rentalRef, {status: 'payment_pending', endStationId: stationId,
      endedAt: admin.firestore.FieldValue.serverTimestamp(), minutes, amountCents: cents});
    return {rentalId, minutes, amountCents: cents};
  });
});

exports.createPayment = onCall({secrets: [stripeKey]}, async (request) => {
  const uid = uidOf(request);
  const rentalId = id(request.data.rentalId);
  const ref = db.collection('rentals').doc(rentalId);
  const rental = await ref.get();
  if (!rental.exists || rental.data().userId !== uid ||
      rental.data().status !== 'payment_pending') {
    throw new HttpsError('failed-precondition', 'Төлөх түрээс олдсонгүй.');
  }
  const stripe = new Stripe(stripeKey.value());
  const intent = await stripe.paymentIntents.create({amount: rental.data().amountCents,
    currency: 'usd', automatic_payment_methods: {enabled: true},
    metadata: {rentalId, userId: uid}}, {idempotencyKey: `rental-${rentalId}`});
  await ref.update({paymentIntentId: intent.id});
  return {clientSecret: intent.client_secret, amountCents: rental.data().amountCents};
});

exports.stripeWebhook = onRequest({secrets: [stripeKey, webhookKey]}, async (req, res) => {
  let event;
  try {
    event = new Stripe(stripeKey.value()).webhooks.constructEvent(
      req.rawBody, req.headers['stripe-signature'], webhookKey.value());
  } catch (_) { res.status(400).send('Invalid signature'); return; }
  if (event.type === 'payment_intent.succeeded') {
    const intent = event.data.object;
    const rentalId = intent.metadata?.rentalId;
    if (rentalId && /^[A-Za-z0-9_-]{1,80}$/.test(rentalId)) {
      const ref = db.collection('rentals').doc(rentalId);
      await db.runTransaction(async (tx) => {
        const rental = await tx.get(ref);
        if (rental.exists && rental.data().status === 'payment_pending' &&
            rental.data().paymentIntentId === intent.id &&
            rental.data().amountCents === intent.amount) {
          tx.update(ref, {status: 'paid', paidAt: admin.firestore.FieldValue.serverTimestamp()});
          const userRef = db.collection('users').doc(rental.data().userId);
          tx.update(userRef, {unpaidRentalId: admin.firestore.FieldValue.delete()});
        }
      });
    }
  }
  res.sendStatus(200);
});
