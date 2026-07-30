import subprocess
import time
import psutil


def remediate(incident, investigation):

    print("\n======================================")
    print("REMEDIATION AGENT STARTED")
    print("======================================")

    print(f"Incident : {incident['incident_id']}")
    print(f"Alert    : {incident['alert']}")

    # --------------------------------------------------
    # For our HighCPU + stress-ng demo
    # --------------------------------------------------

    if incident["alert"] == "HighCPU":

        print("\nApproved remediation:")
        print("Terminate stress-ng processes")

        print("\nExecuting remediation...")

        # Gracefully stop stress-ng
        result = subprocess.run(
            ["pkill", "-TERM", "stress-ng"],
            capture_output=True,
            text=True
        )

        # Give processes time to terminate
        time.sleep(3)

        # --------------------------------------------------
        # Check if stress-ng still exists
        # --------------------------------------------------

        check = subprocess.run(
            ["pgrep", "-a", "stress-ng"],
            capture_output=True,
            text=True
        )

        if check.returncode == 0:

            print("\nstress-ng is still running:")
            print(check.stdout)

            print("\nRemediation FAILED.")

            return False

        print("\nstress-ng processes terminated.")


        # --------------------------------------------------
        # VERIFY CPU
        # --------------------------------------------------

        print("\n======================================")
        print("VERIFYING REMEDIATION")
        print("======================================")

        cpu = psutil.cpu_percent(interval=2)

        print(f"Current CPU utilization: {cpu}%")


        # --------------------------------------------------
        # DETERMINE INCIDENT STATUS
        # --------------------------------------------------

        if cpu < 20:

            print("\n======================================")
            print("REMEDIATION SUCCESSFUL")
            print("======================================")

            print(f"CPU utilization is now {cpu}%")
            print("stress-ng is no longer running.")
            print("Incident can be marked RESOLVED.")

            return True

        else:

            print("\n======================================")
            print("REMEDIATION INCOMPLETE")
            print("======================================")

            print(f"CPU is still high: {cpu}%")
            print("Further investigation is required.")

            return False


    # --------------------------------------------------
    # Unsupported incident
    # --------------------------------------------------

    print(
        f"\nNo automated remediation available "
        f"for alert: {incident['alert']}"
    )

    return False
