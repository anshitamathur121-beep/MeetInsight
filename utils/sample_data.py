# utils/sample_data.py

SAMPLE_REPORT = {
    "metadata": {
        "title": "Q3 Roadmap Review — Growth Pod",
        "date": "Thursday, Jul 2",
        "time": "10:04 AM",
        "duration": "58 min",
        "speakers_count": 5,
        "engine": "Whisper · GPT-4o",
        "processed_time": "Processed in 47s",
        "clarity_score": 87
    },
    "metrics": {
        "decisions_total": 12,
        "decisions_high_impact": 3,
        "actions_total": 9,
        "actions_due_this_week": 5,
        "risks_total": 3,
        "risks_unresolved": 1
    },
    "brief": {
        "summary": "The team green-lit the **checkout redesign for Jul 15 GA**, consolidated analytics on Segment, and moved weekly reviews async — with **Stripe migration timing** as the single unresolved dependency to close by Friday.",
        "tags": ["Checkout GA", "Analytics stack", "Async rituals", "Stripe risk"]
    },
    "decisions": [
        {
            "id": 1,
            "text": "Ship checkout redesign to 100% of NA traffic on Jul 15.",
            "speaker": "Priya",
            "timestamp": "12:41",
            "impact": "High"
        },
        {
            "id": 2,
            "text": "Freeze onboarding scope until Growth cohort report lands.",
            "speaker": "Marcus",
            "timestamp": "24:08",
            "impact": "Medium"
        },
        {
            "id": 3,
            "text": "Consolidate analytics stack on Segment — sunset Heap by Q4.",
            "speaker": "Ada",
            "timestamp": "36:19",
            "impact": "High"
        },
        {
            "id": 4,
            "text": "Move weekly review to async Loom + Friday standup.",
            "speaker": "Team",
            "timestamp": "48:52",
            "impact": "Medium"
        },
        {
            "id": 5,
            "text": "Assign stripe migration sync to engineering leads.",
            "speaker": "Priya",
            "timestamp": "43:10",
            "impact": "Medium"
        },
        {
            "id": 6,
            "text": "Finalize legal review timeline for marketing pages.",
            "speaker": "Ada",
            "timestamp": "46:00",
            "impact": "Medium"
        },
        {
            "id": 7,
            "text": "Deprecate old onboarding API by mid-August.",
            "speaker": "Jonas",
            "timestamp": "51:30",
            "impact": "Medium"
        },
        {
            "id": 8,
            "text": "Establish monthly performance review cadence.",
            "speaker": "Priya",
            "timestamp": "53:00",
            "impact": "Low"
        },
        {
            "id": 9,
            "text": "Begin Segment schema mapping workshop.",
            "speaker": "Ada",
            "timestamp": "55:10",
            "impact": "Low"
        },
        {
            "id": 10,
            "text": "Schedule follow-up sync for Stripe migration on July 10.",
            "speaker": "Priya",
            "timestamp": "57:00",
            "impact": "Medium"
        },
        {
            "id": 11,
            "text": "Deploy beta checkout redesign to internal staging.",
            "speaker": "Priya",
            "timestamp": "13:30",
            "impact": "High"
        },
        {
            "id": 12,
            "text": "Cap marketing experiments budget for Q3.",
            "speaker": "Noor",
            "timestamp": "30:00",
            "impact": "Low"
        }
    ],
    "action_items": [
        {
            "id": 1,
            "text": "Draft rollout comms for checkout GA",
            "assignee": "Priya",
            "due_date": "due Jul 8",
            "priority": "High",
            "completed": False
        },
        {
            "id": 2,
            "text": "Pull churn cohort by acquisition source",
            "assignee": "Ada",
            "due_date": "due Jul 5",
            "priority": "High",
            "completed": True
        },
        {
            "id": 3,
            "text": "Schedule pricing workshop with Finance",
            "assignee": "Marcus",
            "due_date": "due Jul 10",
            "priority": "Medium",
            "completed": False
        },
        {
            "id": 4,
            "text": "Wire Segment events for onboarding v3",
            "assignee": "Jonas",
            "due_date": "due Jul 12",
            "priority": "Medium",
            "completed": False
        },
        {
            "id": 5,
            "text": "Post decisions to #product-updates",
            "assignee": "Priya",
            "due_date": "due Today",
            "priority": "High",
            "completed": False
        },
        {
            "id": 6,
            "text": "Confirm infra team's Q3 capacity for Stripe migration",
            "assignee": "Marcus",
            "due_date": "due Jul 7",
            "priority": "High",
            "completed": False
        },
        {
            "id": 7,
            "text": "Schedule legal review check for checkout copy",
            "assignee": "Ada",
            "due_date": "due Jul 9",
            "priority": "Medium",
            "completed": False
        },
        {
            "id": 8,
            "text": "Send updated calendar invites for async Loom ritual",
            "assignee": "Priya",
            "due_date": "due Jul 6",
            "priority": "Low",
            "completed": True
        },
        {
            "id": 9,
            "text": "Compile Heap event schema list",
            "assignee": "Noor",
            "due_date": "due Jul 8",
            "priority": "Low",
            "completed": False
        }
    ],
    "risks": [
        {
            "id": 1,
            "title": "Stripe migration timing",
            "description": "Depends on infra team's Q3 capacity — not confirmed.",
            "impact": "High",
            "severity": "High"
        },
        {
            "id": 2,
            "title": "Analytics parity gap",
            "description": "Heap event schema doesn't map 1:1 to Segment.",
            "impact": "Medium",
            "severity": "Medium"
        },
        {
            "id": 3,
            "title": "Q3 engineering timeline compression",
            "description": "Onboarding v3 scope is aggressive, which may compress QA cycles.",
            "impact": "Low",
            "severity": "Medium"
        }
    ],
    "changes": [
        {
            "id": 1,
            "title": "Move loyalty tier out of Q3",
            "requestor": "Marcus L.",
            "timestamp": "22:14",
            "priority": "P1",
            "impact": "High"
        },
        {
            "id": 2,
            "title": "Reassign onboarding v3 to Jonas",
            "requestor": "Priya S.",
            "timestamp": "34:02",
            "priority": "P2",
            "impact": "Medium"
        },
        {
            "id": 3,
            "title": "Add legal review step to checkout copy",
            "requestor": "Ada C.",
            "timestamp": "45:37",
            "priority": "P2",
            "impact": "Medium"
        }
    ],
    "questions": [
        {
            "id": 1,
            "text": "Do we need legal sign-off on the new checkout copy?",
            "speaker": "Marcus"
        },
        {
            "id": 2,
            "text": "What's the fallback if Stripe migration slips?",
            "speaker": "Ada"
        }
    ],
    "timeline": [
        {"timestamp": "00:00", "label": "Kickoff & context", "color": "#9ca3af"},
        {"timestamp": "08:12", "label": "Checkout metrics review", "color": "#3b82f6"},
        {"timestamp": "18:40", "label": "Roadmap trade-offs", "color": "#8b5cf6"},
        {"timestamp": "31:05", "label": "Analytics decision", "color": "#b91c1c"},
        {"timestamp": "42:20", "label": "Stripe migration risk", "color": "#f97316"},
        {"timestamp": "51:18", "label": "Rituals & follow-ups", "color": "#10b981"}
    ],
    "airtime": [
        {"speaker": "Priya S.", "percentage": 34, "color": "#8b5cf6"},
        {"speaker": "Marcus L.", "percentage": 26, "color": "#64748b"},
        {"speaker": "Ada C.", "percentage": 18, "color": "#ef4444"},
        {"speaker": "Jonas R.", "percentage": 14, "color": "#10b981"},
        {"speaker": "Noor K.", "percentage": 8, "color": "#f59e0b"}
    ],
    "transcript": [
        {
            "timestamp": "00:12",
            "speaker": "Priya S.",
            "text": "Alright — let's lock the roadmap for Q3. Priority number one is getting checkout out."
        },
        {
            "timestamp": "08:12",
            "speaker": "Ada C.",
            "text": "Cart conversion is up 6% on the beta cohort. We're within the guardrails."
        },
        {
            "timestamp": "12:41",
            "speaker": "Priya S.",
            "tag": "Decision",
            "text": "Then let's ship the redesign to 100% of NA traffic on Jul 15."
        },
        {
            "timestamp": "18:40",
            "speaker": "Marcus L.",
            "text": "I'd rather trim scope than compress engineering on the analytics side."
        },
        {
            "timestamp": "22:14",
            "speaker": "Marcus L.",
            "tag": "Change request",
            "text": "Can we move loyalty tier out of Q3? It's blocking the migration path."
        },
        {
            "timestamp": "24:08",
            "speaker": "Marcus L.",
            "tag": "Decision",
            "text": "Freeze onboarding scope until the cohort report is in."
        },
        {
            "timestamp": "36:19",
            "speaker": "Ada C.",
            "tag": "Decision",
            "text": "Consolidating on Segment is the clean call — sunset Heap by Q4."
        },
        {
            "timestamp": "42:20",
            "speaker": "Priya S.",
            "tag": "Risk",
            "text": "The Stripe migration timing depends on infra — that's our real risk."
        },
        {
            "timestamp": "48:52",
            "speaker": "Priya S.",
            "tag": "Decision",
            "text": "Weekly reviews move to async Loom, with a Friday standup."
        }
    ],
    "email": {
        "to": "growth-pod@company.com",
        "cc": "",
        "subject": "Q3 Roadmap Review — decisions & next steps",
        "tones": {
            "Concise": "Hi team,\n\nQuick recap of today's roadmap review. We locked in three decisions and one open dependency to close this week.\n\nDecisions\n* Ship checkout redesign to 100% of NA traffic on Jul 15 (Priya).\n* Consolidate analytics on Segment; sunset Heap by Q4 (Ada).\n* Move weekly reviews to async Loom + Friday standup.\n\nOwners & dates in the attached brief.\n\n— Sent via MeetInsight",
            "Warm": "Hi everyone,\n\nHope you're all having a great day! Here is a quick, friendly recap of today's Q3 roadmap review. We've made some wonderful progress and locked in three major decisions for our next steps. Let's make sure we support each other in closing the remaining dependency by Friday!\n\nKey Decisions:\n* We will be shipping the checkout redesign to 100% of NA traffic on Jul 15 (led by Priya).\n* We're consolidating our analytics stack on Segment and will sunset Heap by Q4 (led by Ada).\n* We are moving weekly reviews to async Loom plus a Friday standup to save everyone meeting time!\n\nPlease review the attached brief for owner details and due dates. Let's keep up the amazing work!\n\nBest regards,\nYour MeetInsight Team",
            "Executive": "Team,\n\nFollowing is the executive summary of today's Q3 Roadmap Review:\n\n1. Checkout Redesign: Approved for 100% NA traffic launch on July 15. Owner: Priya.\n2. Analytics Stack Consolidation: Approved migration to Segment. Heap will be retired by Q4. Owner: Ada.\n3. Meeting Cadence: Weekly roadmap reviews will be moved to asynchronous Loom updates combined with a brief Friday standup.\n\nUnresolved Dependency:\nStripe migration timeline remains critical and depends on infra team Q3 capacity. We need confirmation by Friday.\n\nAction items and deadlines are detailed in the attached project report.\n\nSincerely,\nGrowth Pod Leadership",
            "Detailed": "Hi team,\n\nHere is the detailed recap of today's Q3 Roadmap Review meeting. Please read through the items and check your respective action items in the dashboard.\n\nDetailed Decisions:\n1. Checkout GA Redesign: The decision was reached to ship the redesign to 100% of NA traffic on July 15. Priya will drive the deployment plan.\n2. Analytics Architecture: To eliminate parity gaps, we will consolidate on Segment. Heap event schemas do not map 1:1, so we will deprecate Heap by Q4. Ada to lead schema mapping.\n3. Operational Rituals: In order to optimize team collaboration, weekly syncs will transition to async Loom recordings. We will supplement this with a brief, high-alignment Friday standup.\n\nCritical Actions to Watch:\n* Priya: Draft rollout comms for checkout GA by Jul 8.\n* Ada: Pull churn cohort by acquisition source by Jul 5.\n* Marcus: Schedule pricing workshop with Finance by Jul 10.\n* Jonas: Wire Segment events for onboarding v3 by Jul 12.\n* Priya: Post decisions to #product-updates today.\n\nFor any questions or risks regarding Stripe migration capacity, please add comments in the dashboard.\n\nRegards,\nMeetInsight Admin"
        },
        "suggestion": "Consider adding a line asking Marcus to confirm the Stripe migration window by Friday — this is the meeting's only unresolved dependency."
    }
}
