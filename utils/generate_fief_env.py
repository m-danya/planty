from argparse import ArgumentParser
import subprocess
import re


def run_quickstart(admin_email, admin_password):
    command = [
        "docker",
        "run",
        "-i",
        "--rm",
        "ghcr.io/fief-dev/fief:latest",
        "fief",
        "quickstart",
        "--docker",
    ]

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    inputs = f"{admin_email}\n{admin_password}\n{admin_password}\n"
    stdout, _ = process.communicate(inputs)

    return stdout


def prompt_for_credentials():
    admin_email = input("Admin email: ")
    admin_password = input("Admin password: ")
    return admin_email, admin_password


def extract_env_variables(output):
    docker_command = ""
    collecting = False
    command_lines = []
    for line in output.split("\n"):
        if line.startswith("docker run"):
            collecting = True
        if collecting:
            command_lines.append(line)
            if line.endswith("\\"):
                continue
            else:
                break

    docker_command = " ".join(command_lines).replace("\\", "")

    if not docker_command:
        print(f"FAILED:\n\n{output}")
        return {}

    env_vars = {}
    env_pattern = re.compile(r'-e\s*"([^=]+)=([^"]+)"')
    matches = env_pattern.findall(docker_command)
    for key, value in matches:
        if not key.startswith("FIEF_"):
            key = "FIEF_" + key
        key = "PLANTY_" + key
        env_vars[key] = value
    env_vars.update(
        {
            "PLANTY_FIEF_PORT": 8050,
            "PLANTY_FIEF_DOMAIN": "127.0.0.1:8050",
        }
    )
    return env_vars


def main():
    args = parse_args()
    if args.use_dummy_credentials:
        admin_email, admin_password = "admin@email.ru", "dummy_password_for_admin_123"
    else:
        admin_email, admin_password = prompt_for_credentials()
    output = run_quickstart(admin_email, admin_password)
    env_vars = extract_env_variables(output)

    if env_vars:
        for key, value in env_vars.items():
            print(f"{key}={value}")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--use-dummy-credentials", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
