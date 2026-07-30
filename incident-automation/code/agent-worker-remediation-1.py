import redis
import json
import sys
import os


# ==========================================================
# FIND EXISTING INCIDENT DIRECTORY
# ==========================================================

INCIDENT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

sys.path.insert(0, INCIDENT_DIR)


# ==========================================================
# IMPORT EXISTING INVESTIGATOR
# ==========================================================

from investigator import investigate


# ==========================================================
# REDIS CONNECTION
# ==========================================================

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

STREAM_NAME = "incidents"


# ==========================================================
# CHECK REDIS CONNECTION
# ==========================================================

try:

    redis_client.ping()

    print("======================================")
    print("DEVOPS AI AGENT WORKER")
    print("======================================")
    print("Redis connection: OK")
    print(f"Listening to stream: {STREAM_NAME}")
    print("Waiting for incidents...")
    print("======================================")

except Exception as error:

    print("Unable to connect to Redis:")
    print(error)

    sys.exit(1)


# ==========================================================
# START FROM NEW MESSAGES
# ==========================================================

last_id = "$"


# ==========================================================
# CONTINUOUSLY WAIT FOR INCIDENTS
# ==========================================================

while True:

    try:

        # --------------------------------------------------
        # Wait until receiver.py publishes an incident
        # --------------------------------------------------

        messages = redis_client.xread(
            {
                STREAM_NAME: last_id
            },
            block=0,
            count=1
        )


        # --------------------------------------------------
        # Process Redis messages
        # --------------------------------------------------

        for stream_name, entries in messages:

            for message_id, fields in entries:

                last_id = message_id


                # ==========================================
                # NEW INCIDENT
                # ==========================================

                print("\n\n======================================")
                print("NEW INCIDENT EVENT RECEIVED")
                print("======================================")

                print(f"Redis Message ID: {message_id}")


                # ==========================================
                # VALIDATE INCIDENT DATA
                # ==========================================

                if "data" not in fields:

                    print("Invalid incident event.")
                    print("Missing 'data' field.")

                    continue


                # ==========================================
                # READ INCIDENT JSON
                # ==========================================

                incident = json.loads(
                    fields["data"]
                )

                print("\nIncident received:")

                print(
                    json.dumps(
                        incident,
                        indent=2
                    )
                )


                # ==========================================
                # START AI INVESTIGATION
                # ==========================================

                print("\n======================================")
                print("STARTING DEVOPS AI AGENT")
                print("======================================")

                print(
                    f"Incident: "
                    f"{incident.get('incident_id')}"
                )


                try:

                    # --------------------------------------
                    # Call investigator.py
                    # --------------------------------------

                    result = investigate(
                        incident
                    )


                    # ======================================
                    # PRINT INVESTIGATION RESULT
                    # ======================================

                    print("\n======================================")
                    print("AI INVESTIGATION COMPLETED")
                    print("======================================")

                    print(
                        f"Incident: "
                        f"{incident.get('incident_id')}"
                    )

                    print("\nInvestigation Result:\n")

                    print(result)


                    # ======================================
                    # HUMAN APPROVAL
                    # ======================================

                    print("\n======================================")
                    print("REMEDIATION APPROVAL REQUIRED")
                    print("======================================")

                    approval = input(
                        "Do you approve remediation? [yes/no]: "
                    )


                    # ======================================
                    # CHECK HUMAN RESPONSE
                    # ======================================

                    if approval.strip().lower() == "yes":

                        print("\nRemediation APPROVED by operator.")

                        # We will add the actual
                        # remediation agent here next.

                    else:

                        print("\nRemediation REJECTED by operator.")


                    # ======================================
                    # WAIT FOR NEXT INCIDENT
                    # ======================================

                    print("\n======================================")
                    print("WAITING FOR NEXT INCIDENT")
                    print("======================================")


                except Exception as error:

                    print("\n======================================")
                    print("AI INVESTIGATION FAILED")
                    print("======================================")

                    print(
                        f"Incident: "
                        f"{incident.get('incident_id')}"
                    )

                    print("\nError:")

                    print(error)

                    print("\nWaiting for next incident...")


    # ======================================================
    # REDIS CONNECTION ERROR
    # ======================================================

    except redis.exceptions.ConnectionError as error:

        print("\nRedis connection error:")
        print(error)

        print("Worker stopped.")

        break


    # ======================================================
    # CTRL+C
    # ======================================================

    except KeyboardInterrupt:

        print("\nAgent worker stopped.")

        break


    # ======================================================
    # OTHER ERRORS
    # ======================================================

    except Exception as error:

        print("\nUnexpected worker error:")
        print(error)
