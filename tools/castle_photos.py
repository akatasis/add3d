"""
castle_photos.py -- thirty-six photographs of the castle (examples/46_castle.py).

Thirty-six camera positions chosen the way a photographer would walk round
the finished model: the approach over the lake, the gatehouse, the walls,
the courtyard and its trades, the palace inside and out, the donjon with the
treasury, the chapel, the roofs, the harbour with its ships, the road up the
hill, the log houses and the kitchen inside.  Each is rendered with tools/preview.py
(the big model is streamed) to ``<folder>/NN_name.png``.

    python3 tools/castle_photos.py examples/out/castle_full/castle.obj photos
    python3 tools/castle_photos.py castle.obj photos --size 1600 1000 --only 1,7,21
    python3 tools/castle_photos.py castle.obj photos --jobs 2      # in parallel
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview

# name, eye, at, fov (half angle, degrees); y is up, the gate is at +z
PHOTOS = [
    ("01_pilis_nuo_ezero", (72, 31.5, 98), (0, 13.5, 5), 33),                 # the castle on its hill, from the south-east
    ("02_priesaisrys_nuo_kranto", (48, 4, 150), (28, 11, 45), 32),           # from the far shore: the island, the road, the harbour
    ("03_vartai_ir_pakeliamas_tiltas", (0, 14.5, 76), (0, 12.5, 48), 36),     # the gatehouse and the drawbridge
    ("04_grandines_ir_grioviai", (-10, 12.5, 63), (0, 12, 52), 40),       # chains, moat and the gate arch
    ("05_piranijos_tvenkinyje", (-8.3, 10.8, 63.3), (-8.6, 9.3, 57.8), 40),    # piranhas in the moat, leaping by the gate towers
    ("06_siena_virs_skardzio", (-98, 25.5, -42), (-40, 17.5, -20), 40),       # the curtain wall on the cliff side
    ("07_stogai_is_paukscio_skrydzio", (24, 67.5, 34), (0, 20.5, -14), 40),   # the palace roofs from above
    ("08_donzonas", (-36, 13, -6), (-26, 28.5, -33), 40),                 # the donjon from the west side of the yard
    ("09_koplycia", (46, 14.5, -10), (30, 15.5, -16), 40),                    # the chapel and its stained glass
    ("10_rumu_fasadas", (7, 17.5, 31), (0, 13.5, -2), 42),                    # the palace front from the courtyard
    ("11_kiemas_nuo_sienos", (32, 23, 36), (-5, 11.5, 5), 45),            # the courtyard from the wall walk
    ("12_sulinys_ir_fontanas", (19, 13, 18), (11, 11, 16), 45),       # the well and the fountain
    ("13_turgus", (-3, 13, 37), (-12, 11.3, 30), 45),                   # the market
    ("14_kalve", (-25, 12.5, 11), (-34, 11.3, 6), 45),                      # the smithy
    ("15_arklides", (17, 12.5, -32), (10, 11, -40), 45),                  # the stable and the horses
    ("16_patrankos_virs_vartu", (-2.2, 27.6, 58.5), (-0.4, 23.4, 50.3), 50),   # the guns on the roof over the gate, the moat below
    ("17_katapulta", (36, 13, 25), (28, 11.5, 18), 45),                   # the trebuchet
    ("18_sienos_takas", (34.9, 24.1, 34.9), (14, 22.3, 49), 45),          # along the wall walk to the gate towers
    ("19_patranka_bokste", (22.6, 29.2, 48.7), (20.4, 26.8, 54.6), 60),      # a tower top: its gun, the gunner, two shooters
    ("20_vartu_praejimas", (0, 12, 39), (0, 13, 53), 45),             # the gate passage and the portcullis
    ("21_didzioji_sale", (2, 15, -5), (0, 13, -27), 36),              # the great hall towards the throne
    ("22_karalius", (1.5, 12.8, -21), (0, 12.1, -27.5), 28),              # the king on his throne
    ("23_puota", (-3, 13, -7), (-6.5, 11.4, -16), 40),                  # the feast, the fire and the throne
    ("24_zidinys", (-8, 14, -16), (-20.8, 13.5, -16), 40),                # the fireplace
    ("25_sachmatu_etiudas", (17, 12.4, -9.5), (15.3, 11.1, -12.2), 30),   # the chess study: White to play and win
    ("26_koplycios_vidus", (28, 12.7, -9.6), (28, 12, -21), 45),        # inside the chapel
    ("27_kareiviu_miegamasis", (0, 21.8, -8), (0, 20.9, -20), 42),        # the soldiers' dormitory
    ("28_pastoge", (-6, 27, -16), (4, 25.8, -24), 45),                  # the attic and its junk
    ("29_lobynas_ir_drakonas", (-26.8, 13.2, -28.8), (-24.5, 12.1, -33.2), 44),  # the treasury and the dragon
    ("30_valdovo_kambarys", (-21.5, 30.1, -29.5), (-27, 29.5, -33.5), 50),  # the lord's chamber
    ("31_uostas_ir_laivai", (127.4, 12, 72.5), (70, 6, 40), 32),          # the harbour: the wharf, the two ships, the road up
    ("32_karaliaus_laivas", (116.0, 4.6, 45.1), (110.0, 3.3, 46.1), 45),  # the king's ship and the ramp for a horse, from the wharf
    ("33_kelias_i_pili", (27, 11.2, 66), (2, 11.5, 58), 36),              # the paved road along the moat to the drawbridge and the gate
    ("34_rastiniai_nameliai", (3, 11.8, -44), (-8, 10.9, -36), 40),       # log houses behind the palace
    ("35_namelio_vidus", (-0.6, 11.6, -36.8), (-3.0, 10.7, -34.7), 50),   # inside a log house: beds, the table
    ("36_virtuves_vidus", (-42.2, 11.3, -7.7), (-44.5, 10.6, -11.1), 50), # inside the kitchen: the hearth, the cook
]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    src, folder = argv[1], argv[2]
    size = (1600, 1000)
    only = None
    jobs = 1
    i = 3
    while i < len(argv):
        if argv[i] == "--size":
            size = (int(argv[i + 1]), int(argv[i + 2]))
            i += 3
        elif argv[i] == "--only":
            only = set(int(v) for v in argv[i + 1].split(","))
            i += 2
        elif argv[i] == "--jobs":
            jobs = int(argv[i + 1])
            i += 2
        else:
            i += 1
    os.makedirs(folder, exist_ok=True)
    todo = [(n, p) for n, p in enumerate(PHOTOS, 1) if only is None or n in only]
    if jobs > 1:                                       # one process per picture, ``jobs`` at a time
        running = []
        for n, (name, eye, at, fov) in todo:
            cmd = [sys.executable, os.path.abspath(preview.__file__), src, os.path.join(folder, name + ".png"),
                   "--size", str(size[0]), str(size[1]), "--eye"] + [str(v) for v in eye] + \
                  ["--at"] + [str(v) for v in at] + ["--fov", str(fov)]
            running.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL))
            if len(running) >= jobs:
                running.pop(0).wait()
        for p in running:
            p.wait()
    else:
        model = src
        if os.path.getsize(src) <= preview.BIG_FILE:           # a small model is loaded once for all the pictures
            model = preview.add.load(src)
        for n, (name, eye, at, fov) in todo:
            out = preview.render(model, os.path.join(folder, name + ".png"), size, eye=list(eye), at=list(at), fov=fov,
                                 folder=os.path.dirname(os.path.abspath(src)))
            print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
