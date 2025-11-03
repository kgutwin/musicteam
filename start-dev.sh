#!/bin/sh

(cd musicteam && chalice local) &

cd musicteam-nuxt && npm run dev

wait
