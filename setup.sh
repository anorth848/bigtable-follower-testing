#!/usr/bin/env bash

gcloud components update beta
gcloud beta emulators bigtable start &

export BIGTABLE_EMULATOR_HOST=127.0.0.1:8086

cbt -project no-project -instance emulator createtable test "families=something"
