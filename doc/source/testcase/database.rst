..Database


+-----------------------+-----------------------------------------------------+
|Test Case Name         |Gluon Database Functional Test                       |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|Id                     |Gluon Database Test 001                              |
+-----------------------+-----------------------------------------------------+
|Objective              |To verify that Gluon is able to save, delete,        |
|                       |retrieve model object/objects from database.         |
+-----------------------+-----------------------------------------------------+
|Test Items             |gluon.tests.db.test_db.\                             |
|                       |test_connection_create_DBDuplicateEntry()            |
|                       |                                                     |
|                       |gluon.tests.db.test_db.test_connection_get_list()    |
|                       |                                                     |
|                       |gluon.tests.db.test_db.\                             |
|                       |test_connection_get_list_filter()                    |
|                       |                                                     |
|                       |gluon.tests.db.test_db.test_connection_get_by_uuid() |
|                       |                                                     |
|                       |gluon.tests.db.test_db.\                             |
|                       |test_connection_get_by_uuid_notfound()               |
|                       |                                                     |
|                       |gluon.tests.db.test_db.\                             |
|                       |test_connection_get_by_primary_key()                 |
|                       |                                                     |
|                       |gluon.tests.db.test_db.\                             |
|                       |test_connection_get_by_primary_key_notfound()        |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|Environmental          |                                                     |
|requirements &         |Environment can be deployed on bare metal of         |
|Preconditions          |virtualized infrastructure deployment can be         |
|                       |HA or non-HA.                                        |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|Scenario Dependencies  | NA                                                  |
+-----------------------+-----------------------------------------------------+
|Procedural             |Step 1: create model:                                |
|Requirements           |     create two model objects with the same set of   |
|                       |     values                                          |
|                       |     asserting that a DBDuplicateEntry exception is  |
|                       |     raised                                          |
|                       |                                                     |
|                       |Step 2: get list of model objects from database:     |
|                       |     use create to insert two model objects and call |
|                       |     get_list to retrieve them                       |
|                       |     asserting that this list of model objects are   |
|                       |     equal                                           |
|                       |                                                     |
|                       |Step 3: filter list of model object from database:   |
|                       |     use create to insert a model object with given  |
|                       |     name and call get_list with filter to retrieve  |
|                       |     asserting that these two objects are equal      |
|                       |                                                     |
|                       |step 4: get model object by uuid                     |
|                       |     use get_by_uuid with uuid to retrieve model     |
|                       |     object from database                            |
|                       |     asserting that model object's uuid equals       |
|                       |     to uuid                                         |
|                       |                                                     |
|                       |step 5: get model object with invalid uuid           |
|                       |     call get_by_uuid with invalid uuid              |
|                       |     asserting that NotFound exception is raised     |
|                       |                                                     |
|                       |step 6: get model object with primary key            |
|                       |     use get_by_primary_key to retrieve model object |
|                       |     from database                                   |
|                       |     asserting that one model is returned            |
|                       |                                                     |
|                       |step 7: get model object with invalid primary key    |
|                       |     call get_by_primary_key with invalid primary    |
|                       |     asserting that NotFound exception is raised     |
+-----------------------+-----------------------------------------------------+
|Input Specifications   |The parameters needed to execute                     |
|                       |gluon.db.sqlalchemy.api                              |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|Output Specifications  |The responses after executing gluon.db.sqlalchemy.api|
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|Pass/Fail Criteria     |If testcase fails, tox should output errors with      |
|                       |trace.                                               |
|                       |                                                     |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|Test Report            |TBD                                                  |
+-----------------------+-----------------------------------------------------+
