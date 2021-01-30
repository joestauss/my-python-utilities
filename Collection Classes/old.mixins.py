import abc
import json
import collections
import collections.abc

class Taggable():
    """A Taggable object can can be given temporary tags, or be a container for Taggable objects.

    Methods for All Taggables
    -------------------------
        Taggable__init__ --- adds the "tags" attribute to the object.
        Taggable.tag( tag_string)

    Methods and Properties for Taggable Collections
    -----------------------------------------------
        Taggable.taggable_records
        Taggable.all_tags
        Taggable.tag_all( tag_string)
    """ #v
    def __init__( self, *args, tags=set(), **kwargs):
        """Add the tags attribute."""
        super().__init__(*args, **kwargs)
        self.tags = tags

    def tag( self, tag_string):
        """Add the parameter to this TaggableRecord's "tags" set."""
        self.tags.add( tag_string)

    @property
    def taggable_records( self):
        """Return any taggable objects, but raise an error if its not a collection."""
        if not isinstance( self, collections.abc.Collection):
            raise TypeError("The taggable_records property is only available for collections.")
        for record in self:
            if isinstance( record, Taggable):
                yield record

    @property
    def all_tags( self):
        """Return all the tags that are on any record."""
        all_tags = set()
        for record in self.taggable_records:
            all_tags = all_tags | record.tags
        return all_tags

    def tag_all( self, tag_string):
        """Apply a tag to each of the records."""
        for record in self.taggable_records:
            record.tag( tag_string)

class ActionThreadsMixin( Taggable):
    """ActionThreadsMixin enables thead-based actions, such as updating records.  Actions can be flagged to be batched.

    To make an ActionThreads perform an action:
    1)  Choose a tag for that action (EXAMPLE_ACTION_TAG below).
    2)  Write a method to perform the action ( example_method( seld) below).
    3)  Add the following key-value pair:
            ACTION_TAG : CORRESPONDING_METHOD_NAME
        to either the regular_action_tags or batch_action_tags dictionary.
    """ #v1
    @property
    def action_threads(self):
        """Property to return a pair of lists: regular action threads, batched action threads."""
        regular_threads  = []
        batch_threads    = []
        for tag in self.tags:
            if tag in self.regular_action_tags.keys():
                regular_threads.append( threading.Thread( target=self.regular_action_tags[ tag]( self)))
            if tag in self.batch_action_tags.keys():
                batch_threads.append( threading.Thread( target=self.batch_action_tags[ tag]( self)))
        return regular_threads, batch_threads

    def act_on_self( self, VERBOSE=False):
        """Do all available actions for this object."""
        regular_threads, batch_threads = self.action_threads
        PatientThreadManager(regular_threads)(VERBOSE=VERBOSE)
        BatchThreadManager(batch_threads)(VERBOSE=VERBOSE)

    @property
    def updatable_records( self):
        """Return any updatable objects, but raise an error if the object is not a collection."""
        if not isinstance( self, collections.abc.Collection):
            raise TypeError("The updatable_records property is only available for collections.")
        for record in self:
            if isinstance( record, ActionThreadsMixin):
                yield record

    def act_on_records( self, VERBOSE=False):
        """Do all actions on all records in this object."""
        regular_threads = []
        batch_threads   = []
        for record in self.updatable_records:
            regular, batch = record.action_threads
            regular_threads.extend( regular)
            batch_threads.extend( batch)
        PatientThreadManager(regular_threads)(VERBOSE=VERBOSE)
        BatchThreadManager(batch_threads)(VERBOSE=VERBOSE)

    #   Subclasses must implement the following:
    #
    def example_method( self):
        pass

    EXAMPLE_ACTION_TAG = hash( "ACTION TAG - Example.") # a hash to avoid accidental collision

    regular_action_tags = {
        EXAMPLE_ACTION_TAG : example_method
    }
    batch_action_tags = {
    }
    #
    #   End of subclass requirements.
