"""
    Checker tests
"""

import pytest

from pyabac.checker import Checker
from pyabac.conditions.logic import Or
from pyabac.conditions.numeric import Gt
from pyabac.conditions.others import CIDR
from pyabac.conditions.string import Equals, RegexMatch
from pyabac.inquiry import Inquiry
from pyabac.policy import Policy


class TestChecker(object):

    @pytest.mark.parametrize("desc, policy, inquiry, result", [
        ("Policy 1",
         Policy(subjects=[{"$.name": Equals("admin")}]),
         Inquiry(subject={"name": "admin"}),
         False),
        ("Policy 2",
         Policy(subjects=[{"$.name": Equals("admin")}]),
         Inquiry(subject={"name": "admin"},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         False),
        ("Policy 3",
         Policy(subjects=[{"$.name": Equals("admin")}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin"},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         True),
        ("Policy 4",
         Policy(subjects=[{"$.name": Equals("john")}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin"},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         False),
        ("Policy 5",
         Policy(subjects=[{"$.name": Equals("admin"), "$.age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin"},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         False),
        ("Policy 6",
         Policy(subjects=[{"$.name": Equals("admin"), "$.age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         False),
        ("Policy 7",
         Policy(subjects=[{"$.name": Equals("admin"), "$.age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin", "age": 40},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         True),
        ("Policy 8",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "GET"}),
         True),
        ("Policy 9",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Equals("GET")}]),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "PUT"}),
         False),
        ("Policy 10",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Or(Equals("GET"), Equals("PUT"))}]),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "PUT"}),
         True),
        ("Policy 11",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Or(Equals("GET"), Equals("PUT"))}],
                context={"$.ip": CIDR("127.0.0.0/24")}),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "PUT"}),
         False),
        ("Policy 12",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Or(Equals("GET"), Equals("PUT"))}],
                context={"$.ip": CIDR("127.0.0.0/24")}),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "PUT"},
                 context={"ip": "192.168.1.100"}),
         False),
        ("Policy 13",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": Equals("/api/v1/health")}],
                actions=[{"$.method": Or(Equals("GET"), Equals("PUT"))}],
                context={"$.ip": CIDR("127.0.0.0/24")}),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": "/api/v1/health"},
                 action={"method": "PUT"},
                 context={"ip": "127.0.0.10"}),
         True),
        ("Policy 14",
         Policy(subjects=[{"$.name": Equals("admin")}, {"age": Gt(30)}],
                resources=[{"$.url": RegexMatch(".*")}],
                actions=[{"$.method": Or(Equals("GET"), Equals("PUT"))}],
                context={"$.ip": CIDR("127.0.0.0/24")}),
         Inquiry(subject={"name": "admin", "age": 20},
                 resource={"url": ""},
                 action={"method": "PUT"},
                 context={"ip": "127.0.0.10"}),
         True),
    ])
    def test_fits(self, desc, policy, inquiry, result):
        checker = Checker(inquiry)
        assert checker.fits(policy) == result
