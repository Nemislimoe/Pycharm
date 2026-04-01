"""
Integration tests for Space Station Event Manager.
Runs all scenarios directly via Service/Repository layer (no HTTP).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import RoleName, DepartmentName
from repository import RoleRepository, DepartmentRepository, UserRepository, EventRepository
from service import UserService, EventService
from schemas import UserCreate, EventCreate

# ── In-memory test DB ──────────────────────────────────────────────────────────
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()

ok = 0
fail = 0

def check(label: str, passed: bool, detail: str = ""):
    global ok, fail
    icon = "✅" if passed else "❌"
    print(f"  {icon} {label}" + (f"  →  {detail}" if detail else ""))
    if passed:
        ok += 1
    else:
        fail += 1

def expect_error(fn, keyword: str, label: str):
    try:
        fn()
        check(label, False, "Expected error was NOT raised")
    except Exception as e:
        check(label, keyword.lower() in str(e).lower(), str(e)[:80])

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  🚀 SPACE STATION EVENT MANAGER — Integration Tests")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# ── 1. Setup: Roles ───────────────────────────────────────────────────────────
print("1. Seed Roles & Departments")
role_repo = RoleRepository(db)
crew_role = role_repo.create(RoleName.CREW, "Standard crew member")
cmd_role  = role_repo.create(RoleName.COMMANDER, "Station commander")
sci_role  = role_repo.create(RoleName.SCIENTIST, "Research scientist")
check("3 roles created", len(role_repo.get_all()) == 3)

dept_repo = DepartmentRepository(db)
sci_dept  = dept_repo.create(DepartmentName.SCIENTIFIC, "Science lab")
tech_dept = dept_repo.create(DepartmentName.TECHNICAL,  "Engineering bay")
med_dept  = dept_repo.create(DepartmentName.MEDICAL,    "Medical bay")
check("3 departments created", len(dept_repo.get_all()) == 3)

# ── 2. Users ──────────────────────────────────────────────────────────────────
print("\n2. Create Users")
user_svc = UserService(db)
commander = user_svc.create_user(UserCreate(username="commander_kirk", full_name="James Kirk", role_id=cmd_role.id))
scientist = user_svc.create_user(UserCreate(username="spock",          full_name="Mr. Spock",  role_id=sci_role.id))
crew1     = user_svc.create_user(UserCreate(username="scotty",         full_name="Montgomery Scott", role_id=crew_role.id))
crew2     = user_svc.create_user(UserCreate(username="chekov",         full_name="Pavel Chekov",     role_id=crew_role.id))
crew3     = user_svc.create_user(UserCreate(username="sulu",           full_name="Hikaru Sulu",      role_id=crew_role.id))
crew4     = user_svc.create_user(UserCreate(username="uhura",          full_name="Nyota Uhura",      role_id=crew_role.id))
check("6 users created", UserRepository(db).get_all().__len__() == 6)

# Duplicate username
expect_error(
    lambda: user_svc.create_user(UserCreate(username="spock", full_name="Clone", role_id=sci_role.id)),
    "already taken", "Duplicate username rejected"
)

# ── 3. Event creation rules ───────────────────────────────────────────────────
print("\n3. Event Creation (role-based access)")
event_svc = EventService(db)
dt1 = datetime(2157, 3, 10, 9, 0)
dt2 = datetime(2157, 3, 10, 14, 0)
dt3 = datetime(2157, 3, 11, 9, 0)

# Commander can create event for any dept
ev_med = event_svc.create_event(EventCreate(
    title="Medical Briefing", description="Full crew health check",
    date=dt1, department_id=med_dept.id, creator_id=commander.id
))
check("Commander creates Medical event", ev_med.id is not None, f"id={ev_med.id}")

ev_tech = event_svc.create_event(EventCreate(
    title="Engine Maintenance", description="Warp core calibration",
    date=dt2, department_id=tech_dept.id, creator_id=commander.id
))
check("Commander creates Technical event", ev_tech.id is not None)

# Scientist can create Scientific event
ev_sci = event_svc.create_event(EventCreate(
    title="Nebula Analysis", description="Scan results review",
    date=dt3, department_id=sci_dept.id, creator_id=scientist.id
))
check("Scientist creates Scientific event", ev_sci.id is not None)

# Scientist cannot create Medical event
expect_error(
    lambda: event_svc.create_event(EventCreate(
        title="Forbidden Med", description="",
        date=dt3, department_id=med_dept.id, creator_id=scientist.id
    )),
    "Commander", "Scientist blocked from Medical dept"
)

# Crew cannot create Scientific event
expect_error(
    lambda: event_svc.create_event(EventCreate(
        title="Forbidden Sci", description="",
        date=dt3, department_id=sci_dept.id, creator_id=crew1.id
    )),
    "Commander", "Crew blocked from Scientific dept"
)

# ── 4. Scientist recommended events (Medical auto-notify) ─────────────────────
print("\n4. Medical → Scientist recommendation")
from service import _recommended_events
check(
    "Spock (Scientist) has Medical event recommended",
    scientist.id in _recommended_events and ev_med.id in _recommended_events[scientist.id]
)
check(
    "Commander NOT in recommended list",
    commander.id not in _recommended_events
)

# ── 5. Assign users to events ─────────────────────────────────────────────────
print("\n5. Event Assignment")
event_svc.assign_user(commander.id, ev_med.id)
event_svc.assign_user(scientist.id, ev_med.id)
event_svc.assign_user(crew1.id, ev_med.id)
event_svc.assign_user(crew2.id, ev_med.id)
check("4 users assigned to Medical event", len(EventRepository(db).get_by_id(ev_med.id).participants) == 4)

# Duplicate assignment
expect_error(
    lambda: event_svc.assign_user(commander.id, ev_med.id),
    "already assigned", "Duplicate assignment rejected"
)

# Max 5 participants
event_svc.assign_user(crew3.id, ev_med.id)
check("5th user assigned (boundary)", len(EventRepository(db).get_by_id(ev_med.id).participants) == 5)

expect_error(
    lambda: event_svc.assign_user(crew4.id, ev_med.id),
    "5 participants", "6th user rejected (max 5)"
)

# ── 6. Overlapping events ─────────────────────────────────────────────────────
print("\n6. Overlapping events")
# Create second event at same time as ev_tech (dt2)
ev_tech2 = event_svc.create_event(EventCreate(
    title="Navigation Check", description="",
    date=dt2, department_id=tech_dept.id, creator_id=commander.id
))
event_svc.assign_user(crew1.id, ev_tech.id)  # crew1 is now at dt2 in ev_tech

expect_error(
    lambda: event_svc.assign_user(crew1.id, ev_tech2.id),
    "Overlapping", "Overlapping event blocked for crew1"
)

# Different time → OK
ev_tech3 = event_svc.create_event(EventCreate(
    title="Hull Inspection", description="",
    date=datetime(2157, 3, 12, 10, 0), department_id=tech_dept.id, creator_id=commander.id
))
event_svc.assign_user(crew1.id, ev_tech3.id)
check("Non-overlapping event assigned OK", True)

# ── 7. Priority calculation ───────────────────────────────────────────────────
print("\n7. Priority field")
ev_med_fresh = EventRepository(db).get_by_id(ev_med.id)
check(f"Medical event (5 participants) → HIGH", ev_med_fresh.priority.value == "High",
      f"got: {ev_med_fresh.priority.value}")

ev_sci_fresh = EventRepository(db).get_by_id(ev_sci.id)
check(f"Sci event (0 participants) → LOW", ev_sci_fresh.priority.value == "Low",
      f"got: {ev_sci_fresh.priority.value}")

event_svc.assign_user(scientist.id, ev_sci.id)
event_svc.assign_user(commander.id, ev_sci.id)
ev_sci_fresh = EventRepository(db).get_by_id(ev_sci.id)
check(f"Sci event (2 participants) → MEDIUM", ev_sci_fresh.priority.value == "Medium",
      f"got: {ev_sci_fresh.priority.value}")

# ── 8. Sorted output ──────────────────────────────────────────────────────────
print("\n8. Sorted events (priority HIGH→MEDIUM→LOW, then date)")
all_events = EventRepository(db).get_all()
sorted_evs = event_svc.get_sorted_events(all_events)
priorities = [e.priority.value for e in sorted_evs]
# HIGH should come before MEDIUM, MEDIUM before LOW
first_low = next((i for i, p in enumerate(priorities) if p == "Low"), len(priorities))
last_high = max((i for i, p in enumerate(priorities) if p == "High"), default=-1)
check("HIGH events precede LOW events in sorted list", last_high < first_low,
      f"order: {priorities}")

# ── 9. Department & user queries ──────────────────────────────────────────────
print("\n9. Query events by department / user")
dept_events = DepartmentRepository(db).get_events_for_department(med_dept.id)
check("Medical dept has correct events", any(e.id == ev_med.id for e in dept_events))

user_events = UserRepository(db).get_events_for_user(commander.id)
check("Commander is in Medical & Sci events", len(user_events) >= 2)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"  Results: {ok} passed, {fail} failed  {'🎉' if fail == 0 else '⚠️'}")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
sys.exit(0 if fail == 0 else 1)
