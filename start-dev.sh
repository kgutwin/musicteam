#!/bin/sh

(cd musicteam && chalice local --host 0.0.0.0) &

cd musicteam-nuxt && npm run dev

wait
