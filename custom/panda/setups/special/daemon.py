description = 'setup for the execution daemon'
group = 'special'


devices = dict(
    UserDBAuth = device('frm2.proposaldb.Authenticator'),
    Auth       = device('services.daemon.auth.ListAuthenticator',
                         description = 'Authentication device',
                         hashing = 'md5',
                         # first entry is the user name, second the hashed password, third the user level
                         passwd = [('guest', '', 'guest'),
                                   ('panda', '74a499fdf9c679c32549fc0d095cae75', 'user'),
                                   ('admin', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
                                   ('astrid', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                   ('josh', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                   ('florin', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                   ('philipp', '54709903e06a8be9a62a649cc8ec2f1d', 'admin'),
                                   ('petr', '54709903e06a8be9a62a649cc8ec2f1d', 'admin')],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    description = 'Daemon, executing commands and scripts',
                    server = 'phys.panda.frm2',
                    authenticators = ['Auth','UserDBAuth',],
                    loglevel = 'debug',
                    ),
)
