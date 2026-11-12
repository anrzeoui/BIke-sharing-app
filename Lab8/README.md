# Лаборатори 8 — Docker image

Энэ лабораторийн ажил нь репогийн үндсэн хавтсанд байгаа `Dockerfile`, `.dockerignore`, `requirements.txt`, `wsgi.py`, `compose.yaml` файлуудыг ашиглана. `Lab7` хавтас үүсгэхгүй; CI нь `.github/workflows/ci.yml`-д байна.

## 1. Docker шалгах

```powershell
docker --version
docker info
```

## 2. Image бүтээх

Репогийн үндсэн хавтсанд:

```powershell
docker build --progress=plain -t bike-sharing-lab8:1.0 .
```

`Dockerfile` нь эхлээд Python суурь image авч, `/app` ажлын хавтас сонгоно. Дараа нь хамаарлын файлыг хуулж сангуудыг суулгана; үүний дараа кодоо хуулна. Ийм дараалал нь зөвхөн код өөрчлөгдөхөд сан суулгасан давхаргыг дахин ашиглах боломжтой.

## 3. Контейнер ажиллуулах, шалгах

```powershell
docker run --rm --name bike-sharing-lab8 -p 3000:3000 -v bike-instance:/app/instance bike-sharing-lab8:1.0
```

Өөр PowerShell цонхонд:

```powershell
curl.exe -i http://localhost:3000/healthz
docker logs bike-sharing-lab8
docker ps
```

Хөтөчөөр `http://localhost:3000` нээж нүүр хуудас, бүртгэл, нэвтрэлтийг шалгана. Контейнерийг эхний цонхонд `Ctrl+C` дарж зогсооно. `bike-instance` volume нь SQLite өгөгдөл болон session secret-ийг контейнер дахин үүсэхэд хадгална.

## 4. Compose

```powershell
docker compose up --build -d
docker compose ps
docker compose logs web
docker compose down
```

## 5. Давхаргын кэш шалгах

Программын жижиг өөрчлөлт хийсний дараа image-ийг дахин бүтээнэ:

```powershell
docker build --progress=plain -t bike-sharing-lab8:1.0 .
```

Build гаралтаас `RUN pip install` алхам `CACHED` болсныг шалгана. `requirements.txt` өөрчлөгдвөл энэ алхам дахин ажиллана.

