from .. import mongo
from bson.objectid import ObjectId
import pandas as pd
import os

class Vote:
    def __init__(self, **kwargs):
        self._id = kwargs.get("_id")
        self.species_guess = kwargs.get("species_guess")
        self.sighting_id = kwargs.get("sighting_id")
        self.user_id = kwargs.get("user_id")
        self.confidence_level = kwargs.get("confidence_level")
        self.current_app_path = kwargs.get("current_app_path")

    @property
    def id(self):
        return str(self._id)
    
    def save_vote(self):
        vote_data = {
            "species_guess": self.species_guess,
            "sighting_id": self.sighting_id,
            "confidence_level": self.confidence_level,
            "user_id": self.user_id,
        }

        prev_vote = mongo.db.votes.find_one({"sighting_id": self.sighting_id, "user_id": self.user_id})

        if self._id:
            mongo.db.votes.update_one({"_id": self._id}, {"$set": vote_data})
        elif prev_vote:
            mongo.db.votes.update_one({"sighting_id": self.sighting_id, "user_id": self.user_id}, {"$set": vote_data})
            self._id = prev_vote.get("_id") # try to keep it consistent, one vote per sighting per user
        else:
            result = mongo.db.votes.insert_one(vote_data)
            self._id = result.inserted_id

        self.update_sighting_species() # update sighting by votes
        return self
    
    def update_sighting_species(self):
        '''
        update sighting species by voting if applicable
        '''
        sighting = mongo.db.sightings.find_one({"_id": ObjectId(self.sighting_id)})
        if not sighting: # presumably sighting has been deleted, clear votes from mongodb
            mongo.db.votes.delete_many({"sighting_id": self.sighting_id})
        else:
            species_votes = {}
            all_votes = mongo.db.votes.find({"sighting_id": self.sighting_id})
            for vote in all_votes:
                if vote.get('species_guess') not in species_votes:
                    species_votes[vote.get('species_guess')] = 0
                species_votes[vote.get('species_guess')] += vote.get('confidence_level', 1)
            sorted_species = {k: v for k, v in sorted(species_votes.items(), key=lambda item: item[1], reverse=True)}
            # set species to be the top vote, and then alphabetically bc i'm not sure what to do in case
            # of a tie
            winning_species = list(sorted_species.keys())[0]
            # check IUCN, ~5% of common names are duplicates, check for any crit match
            df_path = os.path.join(self.current_app_path, 'databases/full_iucn.tsv')
            full_iucn = pd.read_csv(df_path, delimiter='\t')
            if full_iucn[full_iucn['common_name'] == winning_species]['crit'].sum() > 0:
                mongo.db.sightings.update_one({"_id": ObjectId(self.sighting_id)}, {'$set': {'crit': 1}})
            else:
                mongo.db.sightings.update_one({"_id": ObjectId(self.sighting_id)}, {'$set': {'crit': 0}})

            mongo.db.sightings.update_one({"_id": ObjectId(self.sighting_id)}, {'$set': {'species': winning_species}})






