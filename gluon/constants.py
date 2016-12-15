# Copyright (c) 2016 OpenStack Foundation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Sentinel(object):
    """A constant object that does not change even when copied."""
    def __deepcopy__(self, memo):
        # Always return the same object because this is essentially a constant.
        return self

    def __copy__(self):
        # called via copy.copy(x)
        return self


ATTR_NOT_SPECIFIED = Sentinel()

ATTRIBUTES_TO_UPDATE = 'attributes_to_update'

ACTION_MAP = {'POST': 'create',
              'PUT': 'update',
              'GET': 'get',
              'DELETE': 'delete'}
