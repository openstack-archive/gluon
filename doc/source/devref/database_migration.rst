===========================
Database Migration Strategy
===========================

-------------------------------
What happens on a model change?
-------------------------------

If a model is changed and this change is committed to the repo, a Jenkins
job will vote against the change until a migration file for this change is
also uploaded.

Similar to Neutron migration strategy a script for auto generation is used:
`Neutron Script Auto-generation <http://docs.openstack.org/developer/neutron/devref/alembic_migrations.html#script-auto-generation>`_
The big difference is that Proton will have a YAML model. So a new
auto generate script is needed.


-----------------
Migration Process
-----------------

The migrations in the alembic/versions contain the changes needed to migrate
from older Neutron releases to newer versions. A migration occurs by executing
a script that details the changes needed to upgrade the database. The
migration scripts are ordered so that multiple scripts can run sequentially
to update the database.

The migration process is done in the exact same way as the Neutron
database migration.
See details in the devref:
`Neutron Database Migration <http://docs.openstack.org/developer/neutron/devref/alembic_migrations.html>`_


-------
Testing
-------

Unit test need to be written to verify the changed model. This unit test will be
triggered by a Jenkins job and vote on the commit which changes the model.
