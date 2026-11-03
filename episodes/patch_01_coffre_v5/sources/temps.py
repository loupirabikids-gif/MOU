"""One bounded session time for the clock, timer and elapsed captions."""
from __future__ import annotations
import math

SESSION_SECONDS=1800
CALM_START=16.25


def apply_time_state(s):
    t=s['t']
    if t<CALM_START:elapsed=s['story_elapsed_seconds']
    elif t<22.:elapsed=960.+839.*(t-CALM_START)/(22.-CALM_START)
    elif t<23.:elapsed=1799.+t-22.
    else:elapsed=1800.
    elapsed=max(0,min(SESSION_SECONDS,int(math.floor(elapsed+1e-7))))
    remaining=SESSION_SECONDS-elapsed
    s['story_elapsed_seconds']=elapsed;s['remaining_seconds']=remaining;s['remaining']=remaining
    s['display']=f'{remaining//60:02d}:{remaining%60:02d}'
    s['elapsed_minute']=elapsed//60
    clock=9*3600+elapsed
    s['clock_seconds']=clock;s['clock_display']=f'{clock//3600:02d}:{clock%3600//60:02d}'
    s['time_state']={'session_elapsed':elapsed,'remaining':remaining,'clock_seconds':clock,
                     'start_clock_seconds':9*3600,'session_seconds':SESSION_SECONDS}
    if CALM_START<=t<17.15:s['caption']='LATER...'
    elif 17.15<=t<22.:s['caption']=''
    return s
