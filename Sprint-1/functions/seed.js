// Run once with Firebase Admin credentials: node seed.js
const admin = require('firebase-admin');
admin.initializeApp();
const db = admin.firestore();

async function main() {
  const stations = [
    {id: 'sukhbaatar', name: 'Сүхбаатарын талбай', latitude: 47.9184, longitude: 106.9177,
      bikes: ['BK001', 'BK002'], capacity: 10},
    {id: 'national_park', name: 'Үндэсний цэцэрлэгт хүрээлэн', latitude: 47.9087,
      longitude: 106.9420, bikes: ['BK003', 'BK004'], capacity: 10},
  ];
  const batch = db.batch();
  for (const station of stations) {
    batch.set(db.collection('stations').doc(station.id), {
      name: station.name,
      location: new admin.firestore.GeoPoint(station.latitude, station.longitude),
      availableCount: station.bikes.length, capacity: station.capacity, enabled: true,
    });
    for (const bikeId of station.bikes) {
      batch.set(db.collection('bikes').doc(bikeId), {stationId: station.id, status: 'available'});
    }
  }
  await batch.commit();
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
