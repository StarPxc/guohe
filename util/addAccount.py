import redis


r= redis.Redis(host='127.0.0.1', port=6379, db=0)
r.rpush('vpn_account',{'username':'152210702119','password':'935377012'})
r.rpush('vpn_account',{'username':'152210702112','password':'087290'})
r.rpush('vpn_account',{'username':'152210702118','password':'084217'})
r.rpush('vpn_account',{'username':'152210704109','password':'163024'})
r.rpush('vpn_account',{'username':'162210704212','password':'286264'})