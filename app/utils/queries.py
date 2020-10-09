from utils.date_helpers import get_days_in_range
from utils.query_helpers import do_query, return_first_or_empty
from utils.statement_helpers import parse_statement


def get_search_results(postal_code, street_number, suffix, street_name):
    suffix = suffix.replace(" ", "")
    suffix_query = ""
    postal_code_query = ""

    if postal_code:
        postal_code_query = "AND LOWER(postcode) = LOWER(%(postal_code)s)"

    if street_name:
        postal_code_query = "WHERE LOWER(sttnaam) LIKE LOWER(%(street_name)s)"

    if suffix:
        suffix_query = "WHERE LOWER(suffix) LIKE LOWER(%(suffix)s)"

    query = (
        """
            SELECT
              case_id
            FROM
              (
                SELECT
                  import_wvs.zaak_id AS case_id,
                COALESCE(hsltr, '') || COALESCE(toev, '') AS suffix
                FROM
                  import_wvs
                INNER JOIN
                  import_adres
                ON
                  import_wvs.adres_id = import_adres.adres_id
                AND
                  import_wvs.afs_code is NULL
                """
        + postal_code_query
        + """
                AND
                  hsnr = %(street_number)s
              )
            AS
              case_preselect
            """
        + suffix_query
    )

    args = {
        "postal_code": postal_code,
        "street_name": "%" + street_name + "%",
        # % is added here because of the LIKE sql check
        "suffix": suffix + "%",
        "street_number": street_number,
    }

    case_ids = do_query(query, args)
    case_ids = [case_id["case_id"] for case_id in case_ids]
    cases = [get_case(case_id) for case_id in case_ids]
    cases = [case for case in cases if bool(case)]

    return cases


def get_related_case_ids(case_id):
    query = """
            SELECT DISTINCT ON (import_wvs.zaak_id)
              import_adres.adres_id,
              import_adres.wng_id
            FROM import_adres INNER JOIN import_stadia ON import_adres.adres_id = import_stadia.adres_id
            INNER JOIN import_wvs ON import_stadia.adres_id = import_wvs.adres_id
            AND zaak_id = %(case_id)s
              """

    args = {"case_id": case_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_related_cases(address_id):
    query = """
            SELECT wvs_nr as case_number, zaak_id as case_id, beh_oms AS case_reason
            FROM import_wvs
            WHERE adres_id = %(address_id)s
            AND afs_code is Null
            """

    args = {"address_id": address_id}
    executed_query = do_query(query, args)

    return executed_query


def get_toezichthouder_name(code):
    if code:
        query = """
                SELECT naam FROM bwv_medewerkers where code = %(code)s
                """

        args = {"code": code}
        executed_query = do_query(query, args)
        item = return_first_or_empty(executed_query)

        return item.get("naam", None)

    return None


def get_bwv_hotline_bevinding(wng_id):
    query = """
            SELECT
              toez_hdr1_code,
              toez_hdr2_code,
              bevinding_datum,
              bevinding_tijd,
              hit,
              opmerking,
              volgnr_bevinding
            FROM bwv_hotline_bevinding WHERE wng_id = %(wng_id)s
            ORDER BY volgnr_bevinding ASC
            """

    args = {"wng_id": wng_id}
    results = do_query(query, args)

    # Adds the user's names to the result data
    for result in results:
        toez_hdr1_code = result.get("toez_hdr1_code", None)
        toez_hdr2_code = result.get("toez_hdr2_code", None)

        result["toez_hdr1_naam"] = get_toezichthouder_name(toez_hdr1_code)
        result["toez_hdr2_naam"] = get_toezichthouder_name(toez_hdr2_code)

    return results


def get_bwv_hotline_melding(wng_id):
    query = """
            SELECT
              melding_datum,
              melder_anoniem,
              melder_naam,
              melder_emailadres,
              melder_telnr,
              situatie_schets
            FROM bwv_hotline_melding WHERE wng_id = %(wng_id)s
            ORDER BY melding_datum ASC
            """

    args = {"wng_id": wng_id}
    return do_query(query, args)


def get_bwv_personen(address_id):
    query = """
            SELECT
              naam,
              voorletters,
              geslacht,
              geboortedatum,
              bwv_personen_hist.vestigingsdatum_adres,
              bwv_personen_hist.overlijdensdatum
            FROM bwv_personen_hist
            INNER JOIN bwv_personen
              ON bwv_personen.id = bwv_personen_hist.pen_id
              AND ads_id = %(address_id)s
              AND bwv_personen_hist.vertrekdatum_adres is Null
            ORDER BY vestigingsdatum_adres DESC
            """

    args = {"address_id": address_id}
    return do_query(query, args)


def get_import_adres(wng_id):
    query = """
            SELECT
              sttnaam,
              hsnr,
              hsltr,
              toev,
              postcode,
              sbw_omschr,
              kmrs,
              landelijk_bag
            FROM import_adres WHERE wng_id = %(wng_id)s
            """

    args = {"wng_id": wng_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_import_stadia(case_id):
    query = """
            SELECT
              sta_oms,
              import_stadia.begindatum,
              import_stadia.einddatum,
              peildatum,
              sta_nr,
              CONCAT (import_adres.wng_id, '_', import_wvs.wvs_nr, '_', sta_nr) AS invordering_identificatie
            FROM import_adres INNER JOIN import_stadia ON import_adres.adres_id = import_stadia.adres_id
            INNER JOIN import_wvs ON import_stadia.adres_id = import_wvs.adres_id
            AND stadia_id LIKE %(stadia_id)s
            AND zaak_id = %(case_id)s
            ORDER BY sta_nr DESC
            """

    # Adds the _% to support the LIKE query
    args = {"case_id": case_id, "stadia_id": case_id + "_%"}

    all_stadia = do_query(query, args)

    # Make sure all the open stadia are first in the list
    open_stadia = [stadia for stadia in all_stadia if stadia["einddatum"] is None]
    closed_stadia = [stadia for stadia in all_stadia if stadia["einddatum"] is not None]
    stadia = open_stadia + closed_stadia

    return stadia


def get_case(case_id):
    query = """
            SELECT
              import_wvs.zaak_id AS case_id,
              import_wvs.begindatum AS start_date,
              import_wvs.einddatum AS end_date,
              import_adres.postcode AS postal_code,
              import_adres.sttnaam AS street_name,
              import_adres.hsnr AS street_number,
              import_adres.hsltr AS suffix_letter,
              import_adres.toev AS suffix,
              import_adres.wzs_lon AS lng,
              import_adres.wzs_lat as lat,
              import_stadia.sta_oms AS stadium,
              import_wvs.beh_oms AS case_reason
            FROM
              import_wvs
            INNER JOIN
              import_adres ON import_wvs.adres_id = import_adres.adres_id
            INNER JOIN
              import_stadia ON import_wvs.adres_id = import_stadia.adres_id
            AND
              stadia_id LIKE %(case_id_like)s
            AND import_wvs.zaak_id = %(case_id)s
            ORDER BY
              import_stadia.einddatum DESC, sta_nr DESC
            LIMIT 1
            """

    args = {"case_id_like": case_id + "_%", "case_id": case_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_open_cases(address_id):
    # Note: Our current bwv dump doesn't export the complete history of cases ever
    # So this might not always be accurate (we'll have to check)
    query = """
            SELECT
              COUNT(adres_id) as num_open_cases
            FROM import_wvs
            WHERE adres_id=%(address_id)s AND afs_code is NULL
            """

    args = {"address_id": address_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_case_count(address_id):
    query = """
              SELECT
                MAX(wvs_nr) as num_cases
              FROM import_wvs
              WHERE adres_id=%(address_id)s
            """

    args = {"address_id": address_id}
    executed_query = do_query(query, args)
    return return_first_or_empty(executed_query)


def get_statements(case_id):
    query = """
            SELECT
              mededelingen AS statements
            FROM import_wvs WHERE zaak_id=%(case_id)s
            """

    args = {"case_id": case_id}
    executed_query = do_query(query, args)
    raw_statements = return_first_or_empty(executed_query).get("statements")

    statements = parse_statement(raw_statements) if raw_statements else []

    return statements


def get_case_basics(case_id):
    query = """
            SELECT
              wvs_nr as case_number,
              beh_oms as openings_reden
            FROM import_wvs WHERE zaak_id=%(case_id)s
            """

    args = {"case_id": case_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_bwv_tmp(case_id, adres_id):
    case_count = get_case_count(adres_id)
    case_basics = get_case_basics(case_id)
    open_cases = get_open_cases(adres_id)
    return {**case_count, **case_basics, **open_cases}


def get_rented_days(notified_rentals):
    days = 0
    for notified_rental in notified_rentals:
        check_in = notified_rental["check_in"]
        check_out = notified_rental["check_out"]
        days += get_days_in_range(check_in, check_out)
    return days


def get_bwv_vakantieverhuur(wng_id):
    """
    Returns the current year's notified rentals
    """
    query = """
            SELECT
              datum_aanvang_verhuur as check_in,
              datum_einde_verhuur as check_out
            FROM
              bwv_vakantieverhuur
            WHERE
              date_part('year', datum_einde_verhuur) = date_part('year', CURRENT_DATE)
            AND
              wng_id = %(wng_id)s
            AND
              annuleer_date IS NULL
            ORDER BY check_in
            """

    args = {"wng_id": wng_id}
    query_results = do_query(query, args)
    get_rented_days(query_results)

    return query_results


def get_shortstay_license(wng_id):
    """
    Returns the shortstay license
    """

    query = """
            SELECT shortstay
            FROM bwv_woningen
            WHERE id=%(wng_id)s
            """

    args = {"wng_id": wng_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_is_bnb_declared(wng_id):
    """
    Returns if the adress is currently declared as a bnb
    """

    query = """
            SELECT benb_melding as is_bnb_declared
            FROM bwv_woningen
            WHERE id=%(wng_id)s
            """

    args = {"wng_id": wng_id}
    executed_query = do_query(query, args)

    return return_first_or_empty(executed_query)


def get_rental_information(wng_id):
    notified_rentals = get_bwv_vakantieverhuur(wng_id)
    rented_days = get_rented_days(notified_rentals)
    shortstay_license = get_shortstay_license(wng_id)
    is_bnb_declared = get_is_bnb_declared(wng_id)

    return {
        "notified_rentals": notified_rentals,
        "rented_days": rented_days,
        **shortstay_license,
        **is_bnb_declared,
    }
