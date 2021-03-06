# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
sner tests package
"""

from sner.server import db


def persist_and_detach(model):
    """would persist entity/model and detach. used for testing"""

    db.session.add(model)
    db.session.commit()
    db.session.refresh(model)
    db.session.expunge(model)
    return model
