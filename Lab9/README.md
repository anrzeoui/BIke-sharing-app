# Лаборатори 9 — Minikube Deployment ба Service

Лаборатори 8-ын image-ийг бүтээсэн байх шаардлагатай. Командуудыг репогийн үндсэн хавтсанд ажиллуулна.

## 1. Кластер асаах

```powershell
minikube start --driver=docker
kubectl get nodes
```

## 2. Image ба Secret бэлдэх

```powershell
docker build -t bike-sharing-lab8:1.0 .
minikube image load bike-sharing-lab8:1.0
$secret = python -c "import secrets; print(secrets.token_hex(32))"
kubectl create secret generic bike-sharing-secret --from-literal="BIKE_SECRET_KEY=$secret"
```

Нэг Secret-ийг бүх pod-д хэрэглэснээр хэрэглэгчийн session түлхүүр ижил байна. Secret утгыг репод бүү хадгал.

## 3. Гурван pod ба Service үүсгэх

```powershell
kubectl apply -f Lab9/deployment.yaml
kubectl apply -f Lab9/service.yaml
kubectl rollout status deployment/bike-sharing --timeout=180s
kubectl get pods -l app=bike-sharing -o wide
kubectl get service bike-sharing
```

`READY` төлөвтэй 3 pod харагдах ёстой. `imagePullPolicy: Never` тохиргоо нь Minikube-д ачаалсан локал image-ийг ашиглана.

## 4. Self-healing шалгах

Эхний pod-ийн нэрийг авч устгаад оронд нь шинэ pod үүссэнийг ажиглана:

```powershell
$pod = kubectl get pods -l app=bike-sharing -o jsonpath="{.items[0].metadata.name}"
kubectl delete pod $pod
kubectl get pods -l app=bike-sharing -w
```

Шинэ pod `Running` болон `1/1` болсны дараа `Ctrl+C` дарна. Дараах командаар дахин 3 pod байгааг батална:

```powershell
kubectl get pods -l app=bike-sharing -o wide
```

## 5. Хөтөчөөр шалгах

```powershell
minikube service bike-sharing
```

Хөтөчөөр нээгдсэн хаяг дээр нүүр хуудас харагдах ёстой. `/healthz` зам `{"status":"ok"}` буцаана.

