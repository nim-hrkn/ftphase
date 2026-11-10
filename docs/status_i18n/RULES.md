# Translation rules for the ftphase status page (HTML fragments)

You get a JSON file: {"id": "<html fragment in Japanese>", ...}. Write a JSON file with the SAME keys whose values are the
fragments translated into the target language. Rules:
1. Keep every HTML tag, attribute, entity (&lt; &gt; &amp;), <code>...</code> content, <a href>, numbers, units, file names,
   phase names (fcc, B32, L1_2, Al3Li, B2 ...), chemical formulas, variable names, pk numbers, dates and Slurm ids EXACTLY as
   they are. Translate only the natural-language text between tags. Do not add or remove tags. Do not reorder.
2. Terminology (JA -> EN / ID): 工程 = stage / tahap; 相図 = phase diagram / diagram fasa; 二相域 = two-phase region / daerah
   dua fasa; 共晶 = eutectic / eutektik; 固溶限 = solubility limit (solvus) / batas kelarutan; 融点 = melting point / titik
   leleh; 固相 = solid phase / fasa padat; 液相 = liquid phase / fasa cair; 規則相 = ordered phase / fasa teratur; 凸包 = convex
   hull / selubung cembung; 共通接線 = common tangent / garis singgung bersama; 自由エネルギー = free energy / energi bebas;
   配置エントロピー = configurational entropy / entropi konfigurasi; 振動 = vibrational / vibrasi; 熱力学積分 = thermodynamic
   integration (TI) / integrasi termodinamika (TI); 準調和近似 = quasi-harmonic approximation (QHA) / aproksimasi
   kuasi-harmonik (QHA); 補間 = interpolation / interpolasi; 不変反応 = invariant reaction / reaksi invarian; 掃引 = sweep /
   sapuan; 本番 = production run / run produksi; 計算機 = compute host / host komputasi; 図 N = Fig. N / Gambar N; 表 = table /
   tabel; 節 = section / bagian; 落とし穴 = pitfall / jebakan; 検証 = verification / verifikasi; 誤差 = error / galat;
   ノイズ = noise / derau (noise); 要点 = key points / poin utama.
3. Keep product/package names (calphy, phonopy, icet, AiiDA, LAMMPS, MACE, GRACE, SevenNet, MatterSim, NequIP, DPA4, PET,
   ORCHID, ESPEI, pycalphad, Matbench Discovery) unchanged. Keep "mygarden5" etc. unchanged.
4. SVG <text> fragments (short labels) must stay short: at most ~1.3x the Japanese length in characters; abbreviate if needed.
5. Headings: translate; keep leading numbering ("3.6", "付録 B" -> "Appendix B" / "Lampiran B").
6. Output ONLY the JSON object (UTF-8, ensure_ascii false), nothing else. The JSON must parse.
Target language is given in the task. Indonesian: formal technical register (ilmiah), keep English loanwords where usual in
Indonesian materials-science writing (e.g. "supercell", "fit", "run", "GPU").
