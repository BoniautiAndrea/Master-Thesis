import subprocess
from tqdm import tqdm

DOMAINS = ['no_x_v2']#['novelocity', 'mini', 'simplified', 'domain', 'no_x', 'no_t']
# [x, y, t, vy, vt], vx]
INITS = {
    'novelocity' : [(-4,4), (5,10), (-2,2)],
    'mini' : [(-1,1), (1,2), (-1,1), (-2,0)],
    'simplified' : [(0,2), (1,3), (0,0), (-2,0)],#[(-2,2), (1,3), (-1,1), (-2,0)]
    'domain' : [(-1,1), (2,2), (-1,1), (-1,0), (0,0)],
    'no_x' : [(0,0), (1,2), (-1,1), (-1,1), (-1,1), (0,0)],
    'no_x_v2' : [(-1,1), (1,2), (-1,1), (-1,1), (-1,1), (0,0)],
    'no_t' : [(-1,1), (1,2), (0,0), (-1,0), (0,0), (-1,1)]
    }
"""
def plan_and_write(domain : str, values : list):
    init = 5
    with open(f'domains/{domain}/template.pddl', 'r') as re:
        with open(f'domains/{domain}/temp_prob.pddl', 'w') as wr:
            lines = re.readlines()
            for i, line in enumerate(lines):
                if i == init:
                    line = line.replace('(current_y y_0)', f'(current_y y_{values[1]})')
                    line = line.replace('(current_vy vy_0)', f'(current_vy vy_{values[3]})')
                    if domain == 'no_t':
                        line = line.replace('(current_vx vx_0)', f'(current_vx vx_{values[5]})')
                        line = line.replace('(current_x x_0)', f'(current_x x_{values[0]})')
                    if domain == 'no_x_v2':
                        line = line.replace('(current_x x_0)', f'(current_x x_{values[0]})')
                        line = line.replace('(current_t t_0)', f'(current_t t_{values[2]})')
                        line = line.replace('(current_vt vt_0)', f'(current_vt vt_{values[4]})')
                wr.write(line)
    command = ['./../../../prp/src/prp', './domain.pddl', './temp_prob.pddl', '--dump-policy', '2']
    process = subprocess.Popen(command, shell=False, cwd=f'domains/{domain}', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    process.wait()

    with open(f'domains/{domain}/policy.txt', 'r+') as wr, open(f'domains/{domain}/policy.out', 'r') as re:
        lines_out = re.readlines()
        for i, line_out in enumerate(lines_out):
            if line_out.startswith('If'):
                wr.seek(0)
                found = False
                lines_txt = wr.readlines()
                for j, line_txt in enumerate(lines_txt):
                    if line_out == line_txt:
                        found = True
                        break
                if not found:
                    wr.writelines([lines_out[i-1], lines_out[i], lines_out[i+1]])

if __name__ == '__main__':
    for domain in tqdm(DOMAINS, desc='Domain: '):
        for x in tqdm(range(INITS[domain][0][0], INITS[domain][0][1]+1), desc='x: ', leave=False):
            for y in tqdm(range(INITS[domain][1][0], INITS[domain][1][1]+1), desc=f'x= {x}, y: ', leave=False):
                for t in tqdm(range(INITS[domain][2][0], INITS[domain][2][1]+1), desc=f'y= {y}, t: ', leave=False):
                    for vy in tqdm(range(INITS[domain][3][0], INITS[domain][3][1]+1), desc=f't={t}, vy: ', leave=False):
                        for vt in tqdm(range(INITS[domain][4][0], INITS[domain][4][1]+1), desc=f'vy={vy}, vt: ', leave=False):
                            for vx in tqdm(range(INITS[domain][5][0], INITS[domain][5][1]+1), desc=f'vt={vt}, vx: ', leave=False):
                                plan_and_write(domain, [x,y,t,vy,vt,vx])
"""
DOMAINS = ['x_only', 't_only', 'y_only']#['novelocity', 'mini', 'simplified', 'domain', 'no_x', 'no_t']
# [x, y, t, vy, vt], vx]
INITS = {
    'x_only' : [(-2,2), (0,0), (0,0), (0,0), (0,0), (-2,2)],
    'y_only' : [(0,0), (-1,3), (0,0), (-3,1), (0,0), (0,0)],
    't_only' : [(0,0), (0,0), (-2,2), (0,0), (-2,2), (0,0)]
    }

def plan_and_write(domain : str, values : list):
    init = 5
    with open(f'domains/{domain}/template.pddl', 'r') as re:
        with open(f'domains/{domain}/temp_prob.pddl', 'w') as wr:
            lines = re.readlines()
            for i, line in enumerate(lines):
                if i == init:
                    if domain == 'y_only':
                        line = line.replace('(current_y y_0)', f'(current_y y_{values[1]})')
                        line = line.replace('(current_vy vy_0)', f'(current_vy vy_{values[3]})')
                    if domain == 'x_only':
                        line = line.replace('(current_x x_0)', f'(current_x x_{values[0]})')
                        line = line.replace('(current_vx vx_0)', f'(current_vx vx_{values[2]})')
                    if domain == 't_only':
                        line = line.replace('(current_t t_0)', f'(current_t t_{values[4]})')
                        line = line.replace('(current_vt vt_0)', f'(current_vt vt_{values[5]})')
                wr.write(line)
    command = ['./../../../prp/src/prp', './domain.pddl', './temp_prob.pddl', '--dump-policy', '2']
    process = subprocess.Popen(command, shell=False, cwd=f'domains/{domain}', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    process.wait()

    with open(f'domains/{domain}/policy.txt', 'r+') as wr, open(f'domains/{domain}/policy.out', 'r') as re:
        lines_out = re.readlines()
        for i, line_out in enumerate(lines_out):
            if line_out.startswith('If'):
                wr.seek(0)
                found = False
                lines_txt = wr.readlines()
                for j, line_txt in enumerate(lines_txt):
                    if line_out == line_txt:
                        found = True
                        break
                if not found:
                    wr.writelines([lines_out[i-1], lines_out[i], lines_out[i+1]])

if __name__ == '__main__':
    for domain in tqdm(DOMAINS, desc='Domain: '):
        for x in tqdm(range(INITS[domain][0][0], INITS[domain][0][1]+1), desc='x: ', leave=False):
            for y in tqdm(range(INITS[domain][1][0], INITS[domain][1][1]+1), desc=f'x= {x}, y: ', leave=False):
                for t in tqdm(range(INITS[domain][2][0], INITS[domain][2][1]+1), desc=f'y= {y}, t: ', leave=False):
                    for vy in tqdm(range(INITS[domain][3][0], INITS[domain][3][1]+1), desc=f't={t}, vy: ', leave=False):
                        for vt in tqdm(range(INITS[domain][4][0], INITS[domain][4][1]+1), desc=f'vy={vy}, vt: ', leave=False):
                            for vx in tqdm(range(INITS[domain][5][0], INITS[domain][5][1]+1), desc=f'vt={vt}, vx: ', leave=False):
                                plan_and_write(domain, [x,y,vx,vy,t,vt])