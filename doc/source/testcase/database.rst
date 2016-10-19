..Database 


+-----------------------+----------------------------------------------------------------------------------------------------+
|test case name         |Test Gluon database functional test							                                     |
|                       |                                                                                                    |
+-----------------------+----------------------------------------------------------------------------------------------------+
|id                     |Gluon database test 001                                                                             |
+-----------------------+----------------------------------------------------------------------------------------------------+
|objective              |To verify that Gluon is able to save, delete, retrieve model object/objects from database           |
+-----------------------+----------------------------------------------------------------------------------------------------+
|test items             |gluon.tests.db.test_db.test_connection_create_DBDuplicateEntry()                                    |
|                       |                                                                                                    |
|                       |gluon.tests.db.test_db.test_connection_get_list()                                                   |
|                       |                                                                                                    |
|                       |gluon.tests.db.test_db.test_connection_get_list_filter()                                            |
|                       |                                                                                                    |
|                       |gluon.tests.db.test_db.test_connection_get_by_uuid()                                                |
|                       |                                                                                                    |
|                       |gluon.tests.db.test_db.test_connection_get_by_uuid_notfound()                                       |
|                       |                                                                                                    |
|                       |gluon.tests.db.test_db.test_connection_get_by_primary_key()                                         |
|                       |                                                                                                    |
|                       |gluon.tests.db.test_db.test_connection_get_by_primary_key_notfound()                                |
|                       |                                                                                                    |
+-----------------------+----------------------------------------------------------------------------------------------------+
|environmental          |                                                                                                    |
|requirements &         | environment can be deployed on bare metal of virtualized infrastructure                            |
|preconditions          | deployment can be HA or non-HA                                                                     |
|                       |                                                                                                    |
+-----------------------+----------------------------------------------------------------------------------------------------+
|scenario dependencies  | NA                                                                                                 |
+-----------------------+----------------------------------------------------------------------------------------------------+
|procedural             |Step 1: create model:                                                                               |
|requirements           |     create two model objects with the same set of values                                           |
|                       |     asserting that DBDuplicateEntry exception raise                                                |
|                       |                                                                                                    |
|                       |Step 2: get list of model objects from database:                                                    |
|                       |     use create to insert two model objects and call get_list to retrieve them                      |
|                       |     asserting that this list of model objects are equal                                            |
|                       |                                                                                                    |
|                       |Step 3: filter list of model object from database:                                                  |
|                       |     use create to insert an model object with given name and call get_list with filter to retrieve |
|                       |     asserting that these two objects are equal                                                     |
|                       |                                                                                                    |
|                       |step 4: get model object by uuid                                                                    |
|                       |     use get_by_uuid with uuid to retrieve model object from database                               |
|                       |     asserting that model object's uuid equals to uuid                                              |
|                       |                                                                                                    |
|                       |step 5: get model object with invalid uuid                                                          |
|                       |     call get_by_uuid with invalid uuid                                                             |
|                       |     asserting that NotFound exception is raise                                                     |
|                       |                                                                                                    |
|                       |step 6: get modle object with primary key                                                           |
|                       |     use get_by_primary_key to retrieve model object from database                                  |
|                       |     asserting that one model is returned                                                           |
|                       |                                                                                                    |
|                       |step 7: get model object with invalid primary key                                                   |
|                       |     call get_by_primary_key with invalid primary                                                   |
|                       |     asserting that NotFound exception is raise                                                     |
+-----------------------+----------------------------------------------------------------------------------------------------+
|input specifications   |The parameters needed to execute gluon.db.sqlalchemy.api                                            |
|                       |                                                                                                    |
+-----------------------+----------------------------------------------------------------------------------------------------+
|output specifications  |The responses after executing gluon.db.sqlalchemy.api                                               |
|                       |                                                                                                    |
+-----------------------+----------------------------------------------------------------------------------------------------+
|pass/fail criteria     |If testcase fail, tox should output errors with trace                                               |
|                       |                                                                                                    |
|                       |                                                                                                    |
+-----------------------+----------------------------------------------------------------------------------------------------+
|test report            |TBD                                                                                                 |
+-----------------------+----------------------------------------------------------------------------------------------------+

