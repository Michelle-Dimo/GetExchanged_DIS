#!/bin/sh

echo "Waiting for database..."

until flask init-db
do
    echo "Database not ready yet..."
    sleep 2
done

echo "Database initialized"

exec flask --app app run --host=0.0.0.0 --debug