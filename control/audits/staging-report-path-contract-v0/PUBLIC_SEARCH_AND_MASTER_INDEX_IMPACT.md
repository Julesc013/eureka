# Public Search And Master Index Impact

Staging Report Path Contract v0 has no public search impact and no master index
impact.

Public search must not read local report roots by default. `site/dist` must not
receive local/private reports. A report path decision does not submit anything
to a master index and does not accept contribution records.
