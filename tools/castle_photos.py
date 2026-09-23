"""
castle_photos.py -- thirty photographs of the castle (examples/46_castle.py).

Thirty camera positions chosen the way a photographer would walk round the
finished model: the approach over the lake, the gatehouse, the walls, the
courtyard and its trades, the palace inside and out, the donjon with the
treasury, the chapel, the roofs.  Each is rendered with tools/preview.py
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
    ("01_pilis_nuo_ezero", (72, 36, 98), (0, 18, 5), 33),                 # the castle on its hill, from the south-east
    ("02_priesaisrys_nuo_kranto", (14, 3.5, 150), (0, 24, 30), 32),       # from the far shore: lake, jetty, road, gate
    ("03_vartai_ir_pakeliamas_tiltas", (0, 19, 76), (0, 17, 48), 36),     # the gatehouse and the drawbridge
    ("04_grandines_ir_grioviai", (-10, 17, 63), (0, 16.5, 52), 40),       # chains, moat and the gate arch
    ("05_griovys_is_sono", (22, 21, 78), (-6, 15, 56), 30),               # the moat and the bridge from the side
    ("06_siena_virs_skardzio", (-98, 30, -42), (-40, 22, -20), 40),       # the curtain wall on the cliff side
    ("07_stogai_is_paukscio_skrydzio", (24, 72, 34), (0, 25, -14), 40),   # the palace roofs from above
    ("08_donzonas", (-36, 17.5, -6), (-26, 33, -33), 40),                 # the donjon from the west side of the yard
    ("09_koplycia", (46, 19, -10), (30, 20, -16), 40),                    # the chapel and its stained glass
    ("10_rumu_fasadas", (7, 22, 31), (0, 18, -2), 42),                    # the palace front from the courtyard
    ("11_kiemas_nuo_sienos", (32, 27.5, 36), (-5, 16, 5), 45),            # the courtyard from the wall walk
    ("12_sulinys_ir_fontanas", (19, 17.5, 18), (11, 15.5, 16), 45),       # the well and the fountain
    ("13_turgus", (-3, 17.5, 37), (-12, 15.8, 30), 45),                   # the market
    ("14_kalve", (-25, 17, 11), (-34, 15.8, 6), 45),                      # the smithy
    ("15_arklides", (17, 17, -32), (10, 15.5, -40), 45),                  # the stable and the horses
    ("16_patrankos_prie_vartu", (15, 17.8, 33), (7.5, 15.6, 41), 40),     # the cannons inside the gate
    ("17_katapulta", (19, 17.5, 27), (28, 16, 18), 45),                   # the trebuchet
    ("18_sienos_takas", (34.9, 28.6, 34.9), (14, 26.8, 49), 45),          # along the wall walk to the gate towers
    ("19_bokstas_su_zibintu", (-6, 19, 28), (-20.7, 32, 50), 26),          # a tower top: parapet, lantern, flag
    ("20_vartu_praejimas", (0, 16.5, 39), (0, 17.5, 53), 45),             # the gate passage and the portcullis
    ("21_didzioji_sale", (2, 19.5, -5), (0, 17.5, -27), 36),              # the great hall towards the throne
    ("22_karalius", (1.5, 17.3, -21), (0, 16.6, -27.5), 28),              # the king on his throne
    ("23_puota", (-3, 17.5, -7), (-6.5, 15.9, -16), 40),                  # the feast, the fire and the throne
    ("24_zidinys", (-8, 18.5, -16), (-20.8, 18, -16), 40),                # the fireplace
    ("25_sachmatu_etiudas", (17, 16.9, -9.5), (15.3, 15.6, -12.2), 30),   # the chess study: White to play and win
    ("26_koplycios_vidus", (28, 17.2, -9.6), (28, 16.5, -21), 45),        # inside the chapel
    ("27_kareiviu_miegamasis", (0, 26.3, -8), (0, 25.4, -20), 42),        # the soldiers' dormitory
    ("28_pastoge", (-6, 31.5, -16), (4, 30.3, -24), 45),                  # the attic and its junk
    ("29_lobynas_ir_drakonas", (-26.8, 17.7, -28.8), (-24.5, 16.6, -33.2), 44),  # the treasury and the dragon
    ("30_valdovo_kambarys", (-21.5, 34.6, -29.5), (-27, 34, -33.5), 50),  # the lord's chamber
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
