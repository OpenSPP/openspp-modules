STATE_DRAFT = "draft"
STATE_TO_APPROVE = "to_approve"
STATE_APPROVED = "approved"
STATE_DISTRIBUTED = "distributed"
# STATE_ACTIVE = "active"
STATE_ENDED = "ended"
STATE_CANCELLED = "cancelled"

MANAGER_ELIGIBILITY = 1
MANAGER_CYCLE = 2
MANAGER_PROGRAM = 3
MANAGER_ENTITLEMENT = 4
MANAGER_DEDUPLICATION = 5
MANAGER_NOTIFICATION = 6

MANAGER_MODELS = {
    # "eligibility_managers": {
    #    "g2p.eligibility.manager": "g2p.program_membership.manager.default",
    # },
    "deduplication_managers": {
        "g2p.deduplication.manager": "g2p.deduplication.manager.default",
    },
    "notification_managers": {
        "g2p.program.notification.manager": "g2p.program.notification.manager.sms",
    },
    "program_managers": {
        "g2p.program.manager": "g2p.program.manager.default",
    },
    # "cycle_managers": {
    #    "g2p.cycle.manager": "g2p.cycle.manager.default",
    # },
    # "entitlement_managers": {
    #    "g2p.program.entitlement.manager": "g2p.program.entitlement.manager.default",
    # },
}
