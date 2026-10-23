"""Parsers for the ftphase CalcJobs."""

import io
import json

import numpy as np
from aiida import orm
from aiida.parsers import Parser


class QhaParser(Parser):
    def parse(self, **kwargs):
        ret = self.retrieved
        names = ret.base.repository.list_object_names()
        if "qha_results.json" not in names or "qha_arrays.npz" not in names:
            err = ret.base.repository.get_object_content("qha.err") if "qha.err" in names else ""
            self.logger.error("missing QHA output; stderr tail: " + err[-2000:])
            return self.exit_codes.ERROR_MISSING_OUTPUT
        res = json.loads(ret.base.repository.get_object_content("qha_results.json"))
        with ret.base.repository.open("qha_arrays.npz", "rb") as f:
            npz = np.load(io.BytesIO(f.read()))
            arr = orm.ArrayData()
            for k in npz.files:
                arr.set_array(k, np.asarray(npz[k]))
        self.out("results", orm.Dict(dict=res))
        self.out("arrays", arr)
        return None


class CalphyParser(Parser):
    def parse(self, **kwargs):
        import yaml

        ret = self.retrieved
        repo = ret.base.repository
        folders = [n for n in repo.list_object_names() if repo.get_object(n).file_type.name == "DIRECTORY"]
        report_dir = next((d for d in folders if "report.yaml" in repo.list_object_names(d)), None)
        if report_dir is None:
            log = ""
            for d in folders:
                if "calphy.log" in repo.list_object_names(d):
                    log = repo.get_object_content(f"{d}/calphy.log")
            err = repo.get_object_content("calphy.err") if "calphy.err" in repo.list_object_names() else ""
            text = log[-3000:] + "\n" + err[-3000:]
            self.logger.error("no report.yaml; tail of calphy.log/stderr: " + text)
            if "SolidifiedError" in text or "MeltedError" in text or "solidified" in text.lower() or "melted" in text.lower():
                return self.exit_codes.ERROR_PHASE_CHANGED
            return self.exit_codes.ERROR_NO_REPORT
        rep = yaml.safe_load(repo.get_object_content(f"{report_dir}/report.yaml")) or {}
        rep["calculation_folder"] = report_dir
        self.out("results", orm.Dict(dict=rep))
        mode = str(rep.get("input", {}).get("mode", "")) or ("ts" if "-ts-" in report_dir else "")
        if "temperature_sweep.dat" in repo.list_object_names(report_dir):
            data = np.loadtxt(io.StringIO(repo.get_object_content(f"{report_dir}/temperature_sweep.dat")), ndmin=2)
            arr = orm.ArrayData()
            arr.set_array("temperature", data[:, 0])
            arr.set_array("free_energy", data[:, 1])
            arr.set_array("error", data[:, 2] if data.shape[1] > 2 else np.zeros(len(data)))
            self.out("sweep", arr)
        elif "-ts-" in report_dir or mode == "ts":
            return self.exit_codes.ERROR_NO_SWEEP
        return None
