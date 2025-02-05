import os
import sys

from runner.config import Config
from runner.runners import NotebookRunner, ProcessRunner


def get_filename_extension(filename):
    if "." in filename:
        return filename.split(".")[-1].lower()
    else:
        return ""


def main():

    if "ORCHEST_STEP_UUID" not in os.environ:
        raise Exception("No ORCHEST_STEP_UUID passed as environment variable.")

    if "ORCHEST_PIPELINE_UUID" not in os.environ:
        raise Exception("No ORCHEST_PIPELINE_UUID passed as environment variable.")

    # index 1 contains filename
    if len(sys.argv) < 3:
        raise Exception(
            "Should pass in the working directory (relative to the project dir) and "
            "filename (relative to the project dir) that you want to execute."
        )

    step_uuid = os.environ.get("ORCHEST_STEP_UUID")
    pipeline_uuid = os.environ.get("ORCHEST_PIPELINE_UUID")

    # sys.argv[1] contains the working directory relative to
    # the project dir
    working_dir = os.path.join(Config.PROJECT_DIR, sys.argv[1])

    # sys.argv[2] contains the relative file path
    # (relative to the project directory)
    filename = sys.argv[2]
    file_extension = get_filename_extension(filename)
    file_path = os.path.join(Config.PROJECT_DIR, filename)

    # check if file exists in working directory
    if not os.path.isfile(file_path):
        raise Exception("File doesn't appear to exist in file path '%s'" % (file_path,))

    if file_extension == "ipynb":

        nr = NotebookRunner(pipeline_uuid, step_uuid, working_dir)
        nr.run(file_path)

    elif file_extension in ["py", "r", "sh", "jl", ""]:

        extension_script_mapping = {
            # Explicitely use the Python that contains the user
            # dependencies (otherwise Popen could resolve to the Python
            # inside the "orchestdependencies" environment).
            "py": "/opt/conda/bin/python",
            "r": "Rscript",
            "sh": "sh",
            "jl": "julia",
            "": "sh",
        }

        pr = ProcessRunner(pipeline_uuid, step_uuid, working_dir)
        sys.exit(pr.run(extension_script_mapping[file_extension], file_path))

    else:
        raise Exception(
            "Running files with '%s' extension is not yet supported."
            % (file_extension,)
        )


if __name__ == "__main__":
    main()
