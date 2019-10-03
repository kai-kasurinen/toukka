#

import pprint
import argh

from toukka.hub import Toukka


NAMESPACE = 'discogs'

NAMESPACE_KWARGS = {
    'title': 'Discogs',
    'description': 'discogs, discogs, discogs',
    'help': 'help, help, help'
}


@argh.aliases('artist')
def get_artist_by_id(artist_id):
    '''get artist by id'''
    toukka = Toukka()
    artist = toukka.discogs.artist(artist_id)
    pprint.pprint(artist)
    pprint.pprint(artist.data)


@argh.aliases('release')
def get_release_by_id(release_id):
    '''get release by id'''
    toukka = Toukka()
    release = toukka.discogs.release(release_id)
    pprint.pprint(release)
    pprint.pprint(release.data)


@argh.aliases('master')
def get_master_by_id(master_id):
    '''get master by id'''
    toukka = Toukka()
    master = toukka.discogs.master(master_id)
    pprint.pprint(master)
    pprint.pprint(master.data)


@argh.aliases('label')
def get_label_by_id(release_id):
    '''get release by id'''
    toukka = Toukka()
    label = toukka.discogs.label(label_id)
    pprint.pprint(label)
    pprint.pprint(label.data)


@argh.aliases('user')
def get_user_by_name(username):
    '''get user by name'''
    toukka = Toukka()
    user = toukka.discogs.user(username)
    pprint.pprint(user)
    pprint.pprint(user.data)


@argh.aliases('listing')
def get_listing_by_id(listing_id):
    '''get listing by id'''
    toukka = Toukka()
    listing = toukka.discogs.listing(listing_id)
    pprint.pprint(listing)
    pprint.pprint(listing.data)


@argh.aliases('order')
def get_order_by_id(order_id):
    '''get order by id'''
    toukka = Toukka()
    order = toukka.discogs.order(order_id)
    pprint.pprint(order)
    pprint.pprint(order.data)


@argh.aliases('fee')
def get_fee_for(price, currency='USD'):
    '''get fee for'''
    toukka = Toukka()
    price = toukka.discogs.fee_for(price, currency)
    pprint.pprint(price)
    pprint.pprint(price.data)


def identify():
    '''get user representing the OAuth-authorized user'''
    toukka = Toukka()
    user = toukka.discogs.identify()
    pprint.pprint(user)
    pprint.pprint(user.data)


def search(*query, **fields):
    '''search'''
    toukka = Toukka()
    results = toukka.discogs.search(*query, **fields)
    pprint.pprint(results)
    pprint.pprint(results.count())
    pprint.pprint(results.pages())


#

COMMANDS = [
    get_artist_by_id,
    get_release_by_id,
    get_master_by_id,
    get_label_by_id,
    get_user_by_name,
    get_listing_by_id,
    get_order_by_id,
    get_fee_for,
    identify,
    search]

# END
