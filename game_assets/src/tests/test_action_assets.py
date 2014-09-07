#!/usr/bin/env python

import pygame
from game_assets.object_assets import *
from game_assets.object_assets import ObjectAssets
from game_assets.object_assets import AssetSet
from game_assets.serialization import AssetCollectionXml

def create_object_asset():
    
    player_assets = ObjectAssets()
    print 'Default object assets object %s'%(str(player_assets))
    
    attack_assets = AttackAssets()
    print 'Default attack assets object %s'%(str(attack_assets))
    
def create_asset_collection_xml():
    
    asset_set = AssetSet()
    object_assets = ObjectAssets()
    collection_writer = AssetCollectionXml()
    
    # first rectangle
    num_rects = 4
    rect = pygame.Rect(0,0,10,20)
    for i in range(0,4):
        
        r = rect.copy();
        r.x+=i*num_rects
        object_assets.collision.rectangles.append(r)

    #endfor
    
    # adding object asset to set
    asset_set.object_assets_dict['TEST_ACTION'] = object_assets
    
    # saving to xml
    collection_writer.save([asset_set],'test_asset_collection.xml')   
    
    
    
if __name__ == '__main__':
    
    create_object_asset()
    create_asset_collection_xml()

    