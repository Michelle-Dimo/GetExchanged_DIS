#!/bin/sh

echo "Waiting for database..."

<<<<<<< HEAD
until flask init-db
do
=======
until flask init-db; do
>>>>>>> 8e10534 (changed entrypoint file)
    echo "Database not ready yet..."
    sleep 2
done

echo "Database initialized"

exec flask --app app run --host=0.0.0.0 --debug