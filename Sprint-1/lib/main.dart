import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart' hide Card;
import 'package:geolocator/geolocator.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:mobile_scanner/mobile_scanner.dart' hide GeoPoint;

// Supply --dart-define=STRIPE_PUBLISHABLE_KEY=pk_... when running.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const localFirebase = bool.fromEnvironment('USE_FIREBASE_EMULATOR');
  if (localFirebase) {
    await Firebase.initializeApp(
      options: const FirebaseOptions(
        apiKey: 'demo-api-key',
        appId: '1:1234567890:android:demo',
        messagingSenderId: '1234567890',
        projectId: 'demo-bike-sharing',
      ),
    );
    await FirebaseAuth.instance.useAuthEmulator('10.0.2.2', 9099);
    FirebaseFirestore.instance.useFirestoreEmulator('10.0.2.2', 8080);
    FirebaseFunctions.instance.useFunctionsEmulator('10.0.2.2', 5001);
  } else {
    await Firebase.initializeApp();
  }
  Stripe.publishableKey = const String.fromEnvironment(
    'STRIPE_PUBLISHABLE_KEY',
  );
  runApp(const BikeApp());
}

final auth = FirebaseAuth.instance;
final store = FirebaseFirestore.instance;
final functions = FirebaseFunctions.instance;

class BikeApp extends StatelessWidget {
  const BikeApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Дугуй түрээс',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff087c68)),
      useMaterial3: true,
    ),
    home: StreamBuilder<User?>(
      stream: auth.authStateChanges(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return const AuthPage();
        return const HomePage();
      },
    ),
  );
}

class AuthPage extends StatefulWidget {
  const AuthPage({super.key});
  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final form = GlobalKey<FormState>();
  final name = TextEditingController(),
      email = TextEditingController(),
      password = TextEditingController();
  bool register = false, busy = false;
  @override
  void dispose() {
    name.dispose();
    email.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (!form.currentState!.validate()) return;
    setState(() => busy = true);
    try {
      if (register) {
        final credential = await auth.createUserWithEmailAndPassword(
          email: email.text.trim(),
          password: password.text,
        );
        await store.collection('users').doc(credential.user!.uid).set({
          'fullName': name.text.trim(),
          'email': credential.user!.email,
          'createdAt': FieldValue.serverTimestamp(),
        });
      } else {
        await auth.signInWithEmailAndPassword(
          email: email.text.trim(),
          password: password.text,
        );
      }
    } on FirebaseAuthException catch (e) {
      if (mounted) showError(context, e.message ?? 'Нэвтрэхэд алдаа гарлаа.');
    } catch (e) {
      if (mounted) showError(context, '$e');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(register ? 'Бүртгүүлэх' : 'Нэвтрэх')),
    body: Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: Form(
          key: form,
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              const Icon(Icons.pedal_bike, size: 72, color: Color(0xff087c68)),
              if (register)
                TextFormField(
                  controller: name,
                  decoration: const InputDecoration(labelText: 'Нэр'),
                  validator: (v) =>
                      (v ?? '').trim().isEmpty ? 'Нэрээ оруулна уу' : null,
                ),
              TextFormField(
                controller: email,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(labelText: 'Имэйл'),
                validator: (v) =>
                    RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(v ?? '')
                    ? null
                    : 'Имэйл буруу байна',
              ),
              TextFormField(
                controller: password,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Нууц үг'),
                validator: (v) => (v ?? '').length >= 6
                    ? null
                    : '6-аас дээш тэмдэгт оруулна уу',
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: busy ? null : submit,
                child: Text(register ? 'Бүртгүүлэх' : 'Нэвтрэх'),
              ),
              TextButton(
                onPressed: busy
                    ? null
                    : () => setState(() => register = !register),
                child: Text(
                  register ? 'Нэвтрэх хэсэг рүү' : 'Шинэ бүртгэл үүсгэх',
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

void showError(BuildContext context, String message) =>
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  LatLng? position;
  bool locating = false;
  @override
  void initState() {
    super.initState();
    locate();
  }

  Future<void> locate() async {
    setState(() => locating = true);
    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        return;
      }
      final p = await Geolocator.getCurrentPosition();
      if (mounted) setState(() => position = LatLng(p.latitude, p.longitude));
    } catch (e) {
      if (mounted) showError(context, 'Байршил авах боломжгүй: $e');
    } finally {
      if (mounted) setState(() => locating = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    drawer: Drawer(
      child: SafeArea(
        child: ListView(
          children: [
            const ListTile(title: Text('Дугуй түрээс')),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Гарах'),
              onTap: () async => auth.signOut(),
            ),
          ],
        ),
      ),
    ),
    body: StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: store
          .collection('stations')
          .where('enabled', isEqualTo: true)
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return Center(
            child: Text('Зогсоол уншихад алдаа гарлаа: ${snapshot.error}'),
          );
        }
        if (!snapshot.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final docs = snapshot.data!.docs
            .where((d) => d.data()['location'] is GeoPoint)
            .toList();
        docs.sort(
          (a, b) => distance(
            position,
            a.data()['location'] as GeoPoint,
          ).compareTo(distance(position, b.data()['location'] as GeoPoint)),
        );
        final markers = docs.map((d) {
          final geo = d.data()['location'] as GeoPoint;
          return Marker(
            point: LatLng(geo.latitude, geo.longitude),
            width: 48,
            height: 48,
            child: GestureDetector(
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => StationPage(
                    stationId: d.id,
                    name: '${d.data()['name'] ?? d.id}',
                  ),
                ),
              ),
              child: const Icon(Icons.location_on, color: Colors.red, size: 46),
            ),
          );
        }).toList();
        return Stack(
          children: [
            Positioned.fill(
              child: FlutterMap(
                key: ValueKey(position?.toString() ?? 'default'),
                options: MapOptions(
                  initialCenter:
                      position ??
                      (docs.isNotEmpty
                          ? LatLng(
                              (docs.first.data()['location'] as GeoPoint)
                                  .latitude,
                              (docs.first.data()['location'] as GeoPoint)
                                  .longitude,
                            )
                          : const LatLng(47.9184, 106.9177)),
                  initialZoom: 13,
                ),
                children: [
                  TileLayer(
                    urlTemplate:
                        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    userAgentPackageName: 'com.example.bike_sharing_flutter',
                  ),
                  MarkerLayer(markers: markers),
                  if (position != null)
                    MarkerLayer(
                      markers: [
                        Marker(
                          point: position!,
                          width: 24,
                          height: 24,
                          child: const Icon(
                            Icons.circle,
                            color: Colors.blue,
                            size: 20,
                          ),
                        ),
                      ],
                    ),
                  const RichAttributionWidget(
                    attributions: [
                      TextSourceAttribution('OpenStreetMap contributors'),
                    ],
                  ),
                ],
              ),
            ),
            Positioned(
              top: MediaQuery.paddingOf(context).top + 16,
              left: 16,
              child: StreamBuilder<DocumentSnapshot<Map<String, dynamic>>>(
                stream: store
                    .collection('users')
                    .doc(auth.currentUser!.uid)
                    .snapshots(),
                builder: (context, user) => Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xff237b0a),
                    borderRadius: BorderRadius.circular(32),
                  ),
                  child: Row(
                    children: [
                      const CircleAvatar(
                        backgroundColor: Colors.white,
                        child: Icon(Icons.person_outline, color: Colors.black),
                      ),
                      const SizedBox(width: 10),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${user.data?.data()?['fullName'] ?? 'Хэрэглэгч'}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const Text(
                            'ДУГУЙ ТҮРЭЭС',
                            style: TextStyle(color: Colors.white, fontSize: 11),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Positioned(
              top: MediaQuery.paddingOf(context).top + 16,
              right: 16,
              child: Builder(
                builder: (context) => CircleAvatar(
                  radius: 27,
                  backgroundColor: const Color(0xff237b0a),
                  child: IconButton(
                    icon: const Icon(Icons.menu, color: Colors.white),
                    onPressed: () => Scaffold.of(context).openDrawer(),
                  ),
                ),
              ),
            ),
            Positioned(
              right: 16,
              top: MediaQuery.sizeOf(context).height * .42,
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 27,
                    backgroundColor: const Color(0xff237b0a),
                    child: IconButton(
                      onPressed: () => showStationList(context, docs, position),
                      icon: const Icon(
                        Icons.directions_bike,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  CircleAvatar(
                    radius: 27,
                    backgroundColor: const Color(0xff237b0a),
                    child: IconButton(
                      onPressed: locate,
                      icon: const Icon(Icons.my_location, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
            if (locating)
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: LinearProgressIndicator(),
              ),
            Positioned(
              left: 12,
              right: 12,
              bottom: 104,
              child: const ActiveRentalCard(),
            ),
            Positioned(
              bottom: 28,
              left: 0,
              right: 0,
              child: Center(
                child: FilledButton.icon(
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xff237b0a),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 20,
                    ),
                  ),
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const ScanPage()),
                  ),
                  icon: const Icon(Icons.qr_code_scanner, size: 30),
                  label: const Text('SCAN QR CODE'),
                ),
              ),
            ),
          ],
        );
      },
    ),
  );
}

void showStationList(
  BuildContext context,
  List<QueryDocumentSnapshot<Map<String, dynamic>>> docs,
  LatLng? position,
) => showModalBottomSheet<void>(
  context: context,
  showDragHandle: true,
  builder: (sheet) => SafeArea(
    child: ListView(
      shrinkWrap: true,
      children: [
        const ListTile(title: Text('Ойролцоох зогсоолууд')),
        for (final d in docs)
          ListTile(
            leading: const Icon(Icons.pedal_bike),
            title: Text('${d.data()['name'] ?? d.id}'),
            subtitle: Text('Сул дугуй: ${d.data()['availableCount'] ?? 0}'),
            trailing: Text(
              position == null
                  ? ''
                  : '${(distance(position, d.data()['location'] as GeoPoint) / 1000).toStringAsFixed(1)} км',
            ),
            onTap: () {
              Navigator.pop(sheet);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => StationPage(
                    stationId: d.id,
                    name: '${d.data()['name'] ?? d.id}',
                  ),
                ),
              );
            },
          ),
      ],
    ),
  ),
);

double distance(LatLng? from, GeoPoint to) => from == null
    ? double.infinity
    : Geolocator.distanceBetween(
        from.latitude,
        from.longitude,
        to.latitude,
        to.longitude,
      );

class StationPage extends StatelessWidget {
  final String stationId, name;
  const StationPage({super.key, required this.stationId, required this.name});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(name)),
    body: StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: store
          .collection('bikes')
          .where('stationId', isEqualTo: stationId)
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return Center(
            child: Text('Дугуй уншихад алдаа гарлаа: ${snapshot.error}'),
          );
        }
        if (!snapshot.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final bikes = snapshot.data!.docs
            .where((d) => d.data()['status'] == 'available')
            .toList();
        if (bikes.isEmpty) {
          return const Center(child: Text('Сул дугуй алга.'));
        }
        return ListView(
          children: bikes
              .map(
                (bike) => ListTile(
                  leading: const Icon(Icons.pedal_bike),
                  title: Text('Дугуй ${bike.id}'),
                  subtitle: const Text('Сул · QR кодоор түрээслэнэ'),
                ),
              )
              .toList(),
        );
      },
    ),
  );
}

class ScanPage extends StatefulWidget {
  const ScanPage({super.key});
  @override
  State<ScanPage> createState() => _ScanPageState();
}

class _ScanPageState extends State<ScanPage> {
  bool busy = false;
  Future<void> scanned(String code) async {
    if (busy) return;
    final match = RegExp(r'^bike:([A-Za-z0-9_-]{1,80})$').firstMatch(code);
    if (match == null) {
      showError(context, 'QR кодын формат буруу байна.');
      return;
    }
    setState(() => busy = true);
    try {
      await functions.httpsCallable('startRental').call({
        'bikeId': match.group(1),
      });
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) showError(context, 'Түрээс эхэлсэнгүй: $e');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Дугуйн QR уншуулах')),
    body: Stack(
      children: [
        MobileScanner(
          onDetect: (capture) {
            final value = capture.barcodes.firstOrNull?.rawValue;
            if (value != null) scanned(value);
          },
        ),
        if (busy) const Center(child: CircularProgressIndicator()),
      ],
    ),
  );
}

class ActiveRentalCard extends StatelessWidget {
  const ActiveRentalCard({super.key});
  @override
  Widget build(
    BuildContext context,
  ) => StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
    stream: store
        .collection('rentals')
        .where('userId', isEqualTo: auth.currentUser!.uid)
        .snapshots(),
    builder: (context, snapshot) {
      if (!snapshot.hasData) return const SizedBox.shrink();
      final active = snapshot.data!.docs
          .where((d) => d.data()['status'] == 'active')
          .toList();
      final unpaid = snapshot.data!.docs
          .where((d) => d.data()['status'] == 'payment_pending')
          .toList();
      if (active.isNotEmpty) return RentalTimer(rental: active.first);
      if (unpaid.isNotEmpty) {
        return Card(
          child: ListTile(
            title: const Text('Төлбөр хүлээгдэж байна'),
            subtitle: Text(
              'Дүн: \$${((unpaid.first.data()['amountCents'] as num) / 100).toStringAsFixed(2)}',
            ),
            trailing: FilledButton(
              onPressed: () => pay(context, unpaid.first.id),
              child: const Text('Төлөх'),
            ),
          ),
        );
      }
      return const SizedBox.shrink();
    },
  );
}

class RentalTimer extends StatefulWidget {
  final QueryDocumentSnapshot<Map<String, dynamic>> rental;
  const RentalTimer({super.key, required this.rental});
  @override
  State<RentalTimer> createState() => _RentalTimerState();
}

class _RentalTimerState extends State<RentalTimer> {
  Timer? timer;
  bool busy = false;
  @override
  void initState() {
    super.initState();
    timer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  Future<void> finish() async {
    final stations = await store
        .collection('stations')
        .where('enabled', isEqualTo: true)
        .get();
    if (!mounted) return;
    final stationId = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('Буцаах зогсоол'),
        children: stations.docs
            .where(
              (d) =>
                  (d.data()['availableCount'] as num? ?? 0) <
                  (d.data()['capacity'] as num? ?? 0),
            )
            .map(
              (d) => SimpleDialogOption(
                onPressed: () => Navigator.pop(context, d.id),
                child: Text('${d.data()['name'] ?? d.id}'),
              ),
            )
            .toList(),
      ),
    );
    if (stationId == null) return;
    setState(() => busy = true);
    try {
      await functions.httpsCallable('finishRental').call({
        'stationId': stationId,
      });
    } catch (e) {
      if (mounted) showError(context, 'Буцаахад алдаа гарлаа: $e');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final start = (widget.rental.data()['startedAt'] as Timestamp?)?.toDate();
    final minutes = start == null
        ? 0
        : DateTime.now().difference(start).inMinutes + 1;
    return Card(
      child: ListTile(
        title: Text('Идэвхтэй түрээс · ${widget.rental.data()['bikeId']}'),
        subtitle: Text(
          'Хугацаа: $minutes мин · Тооцоолсон төлбөр: \$${(minutes * .50).toStringAsFixed(2)}',
        ),
        trailing: FilledButton(
          onPressed: busy ? null : finish,
          child: const Text('Буцаах'),
        ),
      ),
    );
  }
}

Future<void> pay(BuildContext context, String rentalId) async {
  try {
    if (Stripe.publishableKey.isEmpty) {
      throw Exception('Stripe түлхүүр тохируулаагүй.');
    }
    final result = await functions.httpsCallable('createPayment').call({
      'rentalId': rentalId,
    });
    final secret = result.data['clientSecret'] as String;
    await Stripe.instance.initPaymentSheet(
      paymentSheetParameters: SetupPaymentSheetParameters(
        paymentIntentClientSecret: secret,
        merchantDisplayName: 'Bike Sharing',
      ),
    );
    await Stripe.instance.presentPaymentSheet();
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Төлбөр баталгаажихыг хүлээнэ үү.')),
      );
    }
  } catch (e) {
    if (context.mounted) showError(context, 'Төлбөр хийгдсэнгүй: $e');
  }
}
