import os
import re
import signal
import time
import psutil


# ==========================================================
# EXTRACT PIDs FROM INVESTIGATION RESULT
# ==========================================================

def extract_pids(investigation):

    pids = set()

    # Example:
    # PID 146638
    # PID: 146638
    # PID 146638-146640

    ranges = re.findall(
        r'PID[s]?\s*:?\s*(\d+)\s*-\s*(\d+)',
        investigation,
        re.IGNORECASE
    )

    for start, end in ranges:

        start = int(start)
        end = int(end)

        for pid in range(start, end + 1):
            pids.add(pid)


    # Individual PIDs

    individual_pids = re.findall(
        r'PID[s]?\s*:?\s*(\d+)',
        investigation,
        re.IGNORECASE
    )

    for pid in individual_pids:
        pids.add(int(pid))


    return sorted(pids)


# ==========================================================
# GET INFORMATION ABOUT A PID
# ==========================================================

def get_process_info(pid):

    try:

        process = psutil.Process(pid)

        return {
            "pid": pid,
            "name": process.name(),
            "cmdline": " ".join(process.cmdline()),
            "username": process.username(),
            "exists": True
        }

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):

        return {
            "pid": pid,
            "exists": False
        }


# ==========================================================
# REMEDIATION
# ==========================================================

def remediate(incident, investigation):

    print("\n======================================")
    print("REMEDIATION AGENT STARTED")
    print("======================================")

    print(f"Incident : {incident.get('incident_id')}")
    print(f"Alert    : {incident.get('alert')}")


    # ======================================================
    # STEP 1 - READ INVESTIGATION
    # ======================================================

    print("\nAnalyzing investigation result...")


    # ======================================================
    # STEP 2 - FIND PIDs
    # ======================================================

    pids = extract_pids(
        investigation
    )


    if not pids:

        print("\n======================================")
        print("NO SAFE REMEDIATION IDENTIFIED")
        print("======================================")

        print(
            "The investigation did not identify "
            "specific process PIDs."
        )

        print(
            "Automatic process termination will "
            "NOT be performed."
        )

        return False


    # ======================================================
    # STEP 3 - VERIFY PIDs EXIST
    # ======================================================

    processes = []

    for pid in pids:

        info = get_process_info(pid)

        if info["exists"]:
            processes.append(info)


    if not processes:

        print("\n======================================")
        print("NO TARGET PROCESSES FOUND")
        print("======================================")

        print(
            "The PIDs mentioned in the investigation "
            "are no longer running."
        )

        return False


    # ======================================================
    # STEP 4 - SHOW PROPOSED REMEDIATION
    # ======================================================

    print("\n======================================")
    print("PROPOSED REMEDIATION")
    print("======================================")

    print("\nThe following processes were identified:\n")

    for process in processes:

        print(
            f"PID     : {process['pid']}"
        )

        print(
            f"Process : {process['name']}"
        )

        print(
            f"User    : {process['username']}"
        )

        print(
            f"Command : {process['cmdline']}"
        )

        print("--------------------------------------")


    print("\nProposed Action:")

    print(
        "Send SIGTERM to the above process(es)."
    )

    print(
        "\nSIGTERM requests graceful process termination."
    )


    # ======================================================
    # STEP 5 - SECOND HUMAN APPROVAL
    # ======================================================

    print("\n======================================")
    print("FINAL REMEDIATION APPROVAL REQUIRED")
    print("======================================")

    print(
        "\nWARNING: The processes listed above "
        "will be terminated."
    )

    approval = input(
        "\nExecute this exact remediation? [yes/no]: "
    )


    if approval.strip().lower() != "yes":

        print("\n======================================")
        print("REMEDIATION CANCELLED")
        print("======================================")

        print(
            "Operator rejected final remediation."
        )

        print(
            "No processes were terminated."
        )

        return False


    # ======================================================
    # STEP 6 - EXECUTE REMEDIATION
    # ======================================================

    print("\n======================================")
    print("EXECUTING REMEDIATION")
    print("======================================")


    terminated_pids = []


    for process_info in processes:

        pid = process_info["pid"]

        try:

            process = psutil.Process(pid)

            # Re-read process identity immediately before kill
            current_name = process.name()
            current_cmdline = " ".join(process.cmdline())

            # Protect against PID reuse / changed target
            if (
                current_name != process_info["name"]
                or current_cmdline != process_info["cmdline"]
            ):

                print(
                    f"SKIPPED PID {pid}: "
                    f"process identity changed."
                )

                continue


            print(
                f"Sending SIGTERM to PID {pid} "
                f"({current_name})..."
            )

            os.kill(
                pid,
                signal.SIGTERM
            )

            terminated_pids.append(
                pid
            )


        except psutil.NoSuchProcess:

            print(
                f"PID {pid} already stopped."
            )


        except psutil.AccessDenied:

            print(
                f"Permission denied for PID {pid}."
            )


        except Exception as error:

            print(
                f"Unable to terminate PID {pid}: "
                f"{error}"
            )


    # ======================================================
    # STEP 7 - WAIT
    # ======================================================

    print(
        "\nWaiting for processes to terminate..."
    )

    time.sleep(3)


    # ======================================================
    # STEP 8 - VERIFY PROCESSES
    # ======================================================

    print("\n======================================")
    print("POST-REMEDIATION VERIFICATION")
    print("======================================")


    still_running = []


    for pid in terminated_pids:

        if psutil.pid_exists(pid):

            still_running.append(pid)

            print(
                f"PID {pid}: STILL RUNNING"
            )

        else:

            print(
                f"PID {pid}: TERMINATED"
            )


    # ======================================================
    # STEP 9 - CHECK CPU
    # ======================================================

    print(
        "\nChecking CPU utilization..."
    )

    cpu = psutil.cpu_percent(
        interval=2
    )

    print(
        f"Current CPU utilization: {cpu}%"
    )


    # ======================================================
    # STEP 10 - FINAL RESULT
    # ======================================================

    if not still_running and cpu < 20:

        print("\n======================================")
        print("REMEDIATION SUCCESSFUL")
        print("======================================")

        print(
            "Target processes were terminated."
        )

        print(
            f"CPU utilization is now {cpu}%."
        )

        print(
            "Incident can be marked RESOLVED."
        )

        return True


    print("\n======================================")
    print("REMEDIATION INCOMPLETE")
    print("======================================")

    if still_running:

        print(
            f"Processes still running: "
            f"{still_running}"
        )

    if cpu >= 20:

        print(
            f"CPU is still above threshold: "
            f"{cpu}%"
        )

    print(
        "Further investigation is required."
    )

    return False
