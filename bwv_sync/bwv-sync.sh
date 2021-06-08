#!/usr/bin/env bash
#
# This script will sync the local looplijsten_bwv database from views in the
# data analytics wonen database. It is meant to run from cron. The local tables
# will be TRUNCATE-d before the sync. The views don't contain a lot of data so
# the sync doesn't take long.

# Let's make it easy to ourselves and prevent bash from interpreting the '*' in
# 'select * from ...'
echo "Starting database sync."
set -o noglob
set -euo pipefail

src_host=swdbmams2204.basis.lan
src_db=rve_wonen
src_user=srvc_fixxx
src_pw="${RVE_WONEN_PASSWORD}"
dst_host="${BWV_DB_HOST}"
dst_db="${BWV_DB_NAME}"
dst_user="${BWV_DB_USER}"
dst_pw="${BWV_DB_PASSWORD}"
fraud_prediction_secret_key="${FRAUD_PREDICTION_SECRET_KEY}"
logfile="/tmp/bwv-sync.log"
timestamp_start="$(TZ="Europe/Amsterdam" date "+%Y-%m-%d %H:%M:%S Europe/Amsterdam")"

if test "${ENVIRONMENT}" = "acceptance"; then
  anonymize=true
  url="https://acc.api.top.amsterdam.nl"
else
  anonymize=false
  url="https://api.top.amsterdam.nl"
fi

# The views/tables to sync and the table to sync them to.
# Format: <source view/table>,<destination table>
tables=(
  view_benb_meldingen,bwv_benb_meldingen
  view_hotline_bevinding,bwv_hotline_bevinding
  view_hotline_melding,bwv_hotline_melding
  view_import_adres,import_adres
  view_import_stadia,import_stadia
  view_import_wvs,import_wvs
  view_medewerkers,bwv_medewerkers
  view_personen,bwv_personen
  view_personen_hist,bwv_personen_hist
  view_vakantieverhuur,bwv_vakantieverhuur
  view_woningen,bwv_woningen
)

# These indexes are needed by the vakantieverhuur fraud detection model
indexes=(
  "import_adres__adres_id_idx on import_adres (adres_id)"
  "bwv_personen_hist__ads_id_idx on bwv_personen_hist (ads_id, vestigingsdatum_adres, vertrekdatum_adres)"
  "bwv_personen_hist__pen_id_idx on bwv_personen_hist (pen_id, vestigingsdatum_adres)"
  "import_stadia__stadia_id_idx on import_stadia (stadia_id varchar_pattern_ops)"
  "bwv_hotline_melding__wng_id_idx on bwv_hotline_melding (wng_id)"
  "bwv_personen__id_idx on bwv_personen (id)"
  "import_wvs__adres_id__idx on import_wvs (adres_id)"
)



PGPASSWORD="${dst_pw}" psql -h "$dst_host" -U "$dst_user" -d "$dst_db" -c \
  "CREATE TABLE IF NOT EXISTS sync_log (start timestamp with time zone, finished timestamp with time zone);"
PGPASSWORD="${dst_pw}" psql -h "$dst_host" -U "$dst_user" -d "$dst_db" -c \
  "INSERT INTO sync_log (start) VALUES ('${timestamp_start}');"

# drop indexes
echo "Dropping indexes..."
for index in "${indexes[@]}"; do
  echo "Dropping index ${index}..."
  ixname=$(cut -d ' ' -f 1 <<< "$index")
  PGPASSWORD="${dst_pw}" psql -h "${dst_host}" -U "${dst_user}" -d "$dst_db" -c "DROP INDEX IF EXISTS ${ixname}"
done
echo "Dropping indexes done."


# Sync tables
export PGPASSWORD="${src_pw}"
for src_dst in ${tables[@]}; do
  src_table=$(cut -d, -f 1 <<<"$src_dst")
  dst_table=$(cut -d, -f 2 <<<"$src_dst")
  echo "Syncing $src_table on ${src_host}:${src_db} to $dst_table" | tee "$logfile"

  PGPASSWORD="${dst_pw}" psql -h "${dst_host}" -U "${dst_user}" -c "TRUNCATE $dst_table" "$dst_db"
  psql --no-align --tuples-only -h "$src_host" -d "$src_db" -U "$src_user" \
    -c "COPY (SELECT * FROM $src_table) TO STDOUT" \
    | if $anonymize; then /usr/local/bin/pg_anonymize -c /etc/pg_anonymize.conf "$dst_table"; else cat -; fi \
    | PGPASSWORD="${dst_pw}" psql -h "${dst_host}" -U "${dst_user}" -d "$dst_db" -c "COPY $dst_table FROM STDIN"
done
echo "Syncing tables done."


# (re-)create indexes
echo "Creating indexes..."
for index in "${indexes[@]}"; do
   echo "Creating '${index}'..."
   PGPASSWORD="${dst_pw}" psql -h "${dst_host}" -U "${dst_user}" -d "$dst_db" -c "CREATE INDEX IF NOT EXISTS ${index}"
done
echo "Creating indexes done."

echo "Logging success..."
timestamp_finished="$(TZ="Europe/Amsterdam" date "+%Y-%m-%d %H:%M:%S Europe/Amsterdam")"
PGPASSWORD="${dst_pw}" psql -h "$dst_host" -U "$dst_user" -d "$dst_db" -c \
  "UPDATE sync_log set finished = '${timestamp_finished}' where start = '${timestamp_start}';"
echo "Logging success done."

curl "${url}/api/v1/fraud-prediction/scoring/" \
  -X POST \
  -H "Accept: application/json" \
  -H "Authorization: ${fraud_prediction_secret_key}"
