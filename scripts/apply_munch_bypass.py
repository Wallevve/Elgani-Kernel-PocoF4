#!/usr/bin/env python3
from pathlib import Path

root = Path("kernel")
c = root / "drivers/power/supply/qcom/smb5-lib-munch.c"
h = root / "drivers/power/supply/qcom/smb5-lib-munch.h"

cs = c.read_text()
hs = h.read_text()

def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"[!] {label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)

hs = replace_once(
    hs,
    '#define THERMAL_FCC_OVERRIDE_VOTER  "THERMAL_FCC_OVERRIDE_VOTER"\n',
    '#define THERMAL_FCC_OVERRIDE_VOTER  "THERMAL_FCC_OVERRIDE_VOTER"\n#define BYPASS_VOTER\t\t\t"BYPASS_VOTER"\n',
    "BYPASS_VOTER definition",
)

cs = replace_once(
    cs,
    'bool off_charge_flag;\nstatic bool first_boot_flag;\n',
    'bool off_charge_flag;\nstatic bool first_boot_flag;\nstatic int bypass_charging = 0;\n',
    "bypass_charging variable",
)

old_get = '''int smblib_get_prop_input_suspend(struct smb_charger *chg,
\t\t\t\t  union power_supply_propval *val)
{
\tval->intval
\t\t= (get_client_vote(chg->usb_icl_votable, USER_VOTER) == 0)
\t\t\t || get_client_vote(chg->dc_suspend_votable, USER_VOTER);
\treturn 0;
}
'''
new_get = '''int smblib_get_prop_input_suspend(struct smb_charger *chg,
\t\t\t\t  union power_supply_propval *val)
{
\tif (get_client_vote(chg->chg_disable_votable, BYPASS_VOTER) == 1)
\t\tval->intval = 1;
\telse if (bypass_charging)
\t\tval->intval = 2;
\telse
\t\tval->intval = 0;
\treturn 0;
}
'''
cs = replace_once(cs, old_get, new_get, "input_suspend getter")

old_set = '''int smblib_set_prop_input_suspend(struct smb_charger *chg,
\t\t\t\t  const union power_supply_propval *val)
{
\tint rc;

\t/* vote 0mA when suspended */
\trc = vote(chg->usb_icl_votable, USER_VOTER, (bool)val->intval, 0);
\tif (rc < 0) {
\t\tsmblib_err(chg, "Couldn't vote to %s USB rc=%d\\n",
\t\t\t(bool)val->intval ? "suspend" : "resume", rc);
\t\treturn rc;
\t}

\trc = vote(chg->dc_suspend_votable, USER_VOTER, (bool)val->intval, 0);
\tif (rc < 0) {
\t\tsmblib_err(chg, "Couldn't vote to %s DC rc=%d\\n",
\t\t\t(bool)val->intval ? "suspend" : "resume", rc);
\t\treturn rc;
\t}

\tpower_supply_changed(chg->batt_psy);
\treturn rc;
}
'''
new_set = '''int smblib_set_prop_input_suspend(struct smb_charger *chg,
\t\t\t\t  const union power_supply_propval *val)
{
\tint rc;

\t/* Keep USER suspend votes clear; input_suspend=1 is charger disable,
\t * while input_suspend=2 enables bypass charging.
\t */
\trc = vote(chg->usb_icl_votable, USER_VOTER, false, 0);
\tif (rc < 0) {
\t\tsmblib_err(chg, "Couldn't clear USB suspend vote rc=%d\\n", rc);
\t\treturn rc;
\t}

\trc = vote(chg->dc_suspend_votable, USER_VOTER, false, 0);
\tif (rc < 0) {
\t\tsmblib_err(chg, "Couldn't clear DC suspend vote rc=%d\\n", rc);
\t\treturn rc;
\t}

\tif (val->intval == 1) {
\t\trc = vote(chg->chg_disable_votable, BYPASS_VOTER, true, 0);
\t\tbypass_charging = 0;
\t} else if (val->intval == 2) {
\t\trc = vote(chg->chg_disable_votable, BYPASS_VOTER, false, 0);
\t\tbypass_charging = 1;
\t} else {
\t\trc = vote(chg->chg_disable_votable, BYPASS_VOTER, false, 0);
\t\tbypass_charging = 0;
\t}

\tif (rc < 0) {
\t\tsmblib_err(chg, "Couldn't set input_suspend=%d rc=%d\\n",
\t\t\tval->intval, rc);
\t\treturn rc;
\t}

\tpower_supply_changed(chg->batt_psy);
\treturn rc;
}
'''
cs = replace_once(cs, old_set, new_set, "input_suspend setter")

old_thermal = '''static void smblib_thermal_setting_work(struct work_struct *work)
{
\tstruct smb_charger *chg = container_of(work, struct smb_charger,
\t\t\tthermal_setting_work.work);

\tif (chg->pps_thermal_level > chg->system_temp_level) {
'''
new_thermal = '''static void smblib_thermal_setting_work(struct work_struct *work)
{
\tstruct smb_charger *chg = container_of(work, struct smb_charger,
\t\t\tthermal_setting_work.work);

\tif (bypass_charging)
\t\tchg->pps_thermal_level = 0;

\tif (chg->pps_thermal_level > chg->system_temp_level) {
'''
cs = replace_once(cs, old_thermal, new_thermal, "PPS thermal bypass")

old_temp = '''\tchg->system_temp_level = val->intval;

\tsmblib_dbg(chg, PR_OEM, "thermal level:%d, thermal_levels:%d "
'''
new_temp = '''\tchg->system_temp_level = val->intval;
\tif (bypass_charging)
\t\tchg->system_temp_level = 0;

\tsmblib_dbg(chg, PR_OEM, "thermal level:%d, thermal_levels:%d "
'''
cs = replace_once(cs, old_temp, new_temp, "system thermal bypass")

c.write_text(cs)
h.write_text(hs)
print("[+] Munch bypass charging source modifications applied")
