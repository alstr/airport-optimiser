import argparse
import os
import shutil
import time
from datetime import datetime
import re

v = '1.2'
summary = []


def backup_file(path):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = f'{path}-{ts}.bak'
    shutil.copy2(path, backup)
    print(f'-> Backup created: {backup}')
    return backup


def restore_file(path, name_hint, dry_run=False):
    print(f'Restoring {name_hint}...')
    if not os.path.isfile(path):
        raise FileNotFoundError(f'-> {name_hint} not found at expected location: {path}')

    dir_path = os.path.dirname(path)
    base_name = os.path.basename(path)
    backups = [f for f in os.listdir(dir_path) if f.startswith(base_name) and f.endswith('.bak')]

    if not backups:
        print(f'-> No backups found to restore for {name_hint}')
        print('-----')
        return
    elif len(backups) > 1:
        print(f'-> Multiple backups found for {name_hint}, aborting to avoid overwriting the wrong file')
        print('-> Please remove unwanted backups and retry')
        print('-----')
        return

    backup_path = os.path.join(dir_path, backups[0])
    try:
        if dry_run:
            print(f'-> Backup {backups[0]} would be restored to {path}')
            print('-> Not restoring as dry run is enabled')
            print('-----')
            return
        os.remove(path)
        print(f'-> Deleted modified file: {path}')
        shutil.move(backup_path, path)
        print(f'-> Restored backup to {path}')
    except Exception as restore_ex:
        raise restore_ex

    print(f'-> Completed restore of {name_hint}')
    print('-----')


def clean_apt_dat(path, force=False, dry_run=False):
    print('Starting on airport ground vehicle routes...')
    if not os.path.isfile(path):
        raise FileNotFoundError(f'-> apt.dat not found at expected location: {path}')

    already_clean = True
    skip_codes = ('1400', '1401')
    lines_matched = 0
    with open(path, 'r', encoding='utf-8', newline='') as f:
        print('-> Checking for existing airport ground vehicle routes...')
        for line in f:
            if line.startswith(skip_codes):
                lines_matched += 1
                already_clean = False

    if dry_run:
        if already_clean:
            print(f'-> apt.dat already optimised')
        else:
            summary_line = f'-> apt.dat not optimised, {lines_matched} modifications could be made'
            summary.append(summary_line)
            print(summary_line)
        print('-> Not modifying file as dry run is enabled')
        print('-----')
        return

    if already_clean:
        print('-> No 1400/1401 lines found — file may already be optimised')
        if not force:
            print('-> Aborting to avoid backing up an already optimised file')
            print('-----')
            return
        else:
            print('-> Force running anyway')
    else:
        print('-> File is not optimised')

    if not already_clean:
        backup_file(path)
    lines_removed = 0

    out_path = os.path.join(os.path.dirname(path), 'apt_temp.dat')
    try:
        with (open(path, 'r', encoding='utf-8', newline='') as fin,
              open(out_path, 'w', encoding='utf-8', newline='') as fout):
            for line in fin:
                if not line.startswith(skip_codes):
                    fout.write(line)
                else:
                    lines_removed += 1
        summary_line = (f'-> Removed approx. {lines_removed // 2} airport ground vehicle routes ({lines_removed} '
                        f'line entries) in {path}')
        summary.append(summary_line)
        print(summary_line)
        shutil.move(out_path, path)
    except Exception as apt_ex:
        if os.path.exists(out_path):
            os.remove(out_path)
        raise apt_ex
    print('-----')


def disable_scenery_cars(path, force=False, dry_run=False):
    print('Starting on scenery vehicle density...')
    if not os.path.isfile(path):
        raise FileNotFoundError(f'-> settings.txt not found at expected location: {path}')

    already_clean = False
    with open(path, 'r', encoding='utf-8', newline='') as f:
        print('-> Checking existing vehicle density...')
        lines_matched = 0
        for line in f:
            if line.strip().startswith('SETTING_1 renopt_draw_3d_04') and 'reno/draw_cars_05' in line:
                if re.search(r'reno/draw_cars_05\s+0\s+cars/lod_min\s+0', line):
                    lines_matched += 1
                if lines_matched == 5:  # We assume 5 lines relating to this in settings.txt - valid as of XP12
                    already_clean = True
                    break

    if dry_run:
        if already_clean:
            print(f'-> settings.txt already optimised')
        else:
            summary_line = f'-> settings.txt not optimised, {5 - lines_matched} modifications could be made'
            summary.append(summary_line)
            print(summary_line)
        print('-> Not modifying file as dry run is enabled')
        print('-----')
        return

    if already_clean:
        print('-> Vehicle density already set to 0 — file may already be optimised')
        if not force:
            print('-> Aborting to avoid backing up an already optimised file')
            print('-----')
            return
        else:
            print('-> Force running anyway')
    else:
        print('-> Vehicle density normal')

    if not already_clean:
        backup_file(path)
    lines = []
    with open(path, 'r', encoding='utf-8', newline='') as f:
        for line in f:
            if line.strip().startswith('SETTING_1 renopt_draw_3d_04') and 'reno/draw_cars_05' in line:
                parts = line.split()
                parts[4] = '0'
                parts[-1] = '0'
                line = ' '.join(parts) + '\n'
            lines.append(line)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(lines)
    summary_line = f'-> Scenery vehicle density set to 0 in {path}'
    summary.append(summary_line)
    print(summary_line)
    print('-----')


if __name__ == '__main__':
    try:
        start = time.time()
        print(f'Running Airport Optimiser {v}')
        print(f'For updates and help: '
              f'https://github.com/alstr/airport-optimiser/')

        p = argparse.ArgumentParser(description='Airport Optimiser (run from X-Plane root folder)')
        p.add_argument('-g', action='store_true', help='Remove airport ground vehicles')
        p.add_argument('-w', action='store_true', help='Remove scenery vehicles')
        p.add_argument('-f', action='store_true', help='Force overwrite even if files appear already optimised')
        p.add_argument('-r', action='store_true', help='Restore backups')
        p.add_argument('-d', action='store_true',
                       help='Show what would happen without modifying any files')
        args = p.parse_args()

        xp_path = os.getcwd()
        if (not os.path.isdir(os.path.join(xp_path, 'Global Scenery'))
                or not os.path.isdir(os.path.join(xp_path, 'Resources'))):
            raise FileNotFoundError(f'This does not look like a valid X-Plane root folder: {xp_path}')

        apt_path = os.path.join(xp_path, 'Global Scenery', 'Global Airports', 'Earth nav data', 'apt.dat')
        settings_path = os.path.join(xp_path, 'Resources', 'settings.txt')

        if not (args.g or args.w or args.r):
            raise RuntimeError('No action selected. Use -g, -w, or -r.')

        print('-----')
        if args.r:
            if args.g:
                restore_file(apt_path, 'airport ground vehicles', args.d)
            if args.w:
                restore_file(settings_path, 'scenery vehicles', args.d)
        else:
            if args.g:
                clean_apt_dat(apt_path, args.f, args.d)
            if args.w:
                disable_scenery_cars(settings_path, args.f, args.d)

        concorde_spd = 0.3761
        duration = time.time() - start
        distance = duration * concorde_spd
        if duration < 0.5:
            print(
                f'Airport Optimiser finished in {duration:.2f} seconds '
                f'(about the number of seconds you enjoy on a Ryanair flight)')
        else:
            if len(summary) > 0:
                print('Final results:')
                for s in summary:
                    print(s)
            print(f'Airport Optimiser finished in {duration:.2f} seconds '
                  f'(about the time it took Concorde to travel {distance:.2f} miles)')

    except Exception as e:
        print(f'Error: {e}')
        exit(1)
