
ACCESS_KEY="admin"
if [ -n "$MINIO_ACCESS_KEY" ]; then
    ACCESS_KEY="$MINIO_ACCESS_KEY"
fi

SECRET_KEY="adminadmin"
if [ -n "$MINIO_SECRET_KEY" ]; then
    SECRET_KEY="$MINIO_SECRET_KEY"
fi

docker run \
   --rm \
    -p 9000:9000 \
   -p 9090:9090 \
   --name minio \
   --network de_network \
   -e "MINIO_ROOT_USER=$ACCESS_KEY" \
   -e "MINIO_ROOT_PASSWORD=$SECRET_KEY" \
   quay.io/minio/minio server /data --console-address ":9090"