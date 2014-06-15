#!/usr/bin/perl -w

use DBI;
use strict;


my $mysql_host = "localhost";
my $mysql_user = "user";
my $mysql_pass = "password";
my $mysql_db = "database";
my $dsn = "DBI:mysql:database=$mysql_db;host=$mysql_host";

my $dbh = DBI->connect($dsn, $mysql_user, $mysql_pass ) or die $DBI::errstr;

my @slaves = ( "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4");
my $lag = 0;
my $slave = '';
my $sqlfile = $ARGV[0]; # pass sql file as a variable to the script
my $lag_check_interval = 1000;

sub check_slave_lag {

        foreach(@slaves) {
                $slave = $_;
                my $slave_is_working = 1;
                my $dbhs = DBI->connect("DBI:mysql:database=$mysql_db;host=$slave", $mysql_user, $mysql_pass ) or $slave_is_working = 0;
                if ($slave_is_working == 1) {
                        my $sths = $dbhs->prepare("SHOW SLAVE STATUS") or warn "can't connect";
                        $sths->execute() or warn $DBI::errstr;

                        my $rows = $sths->fetchrow_hashref();
                        $lag = $rows->{'Seconds_Behind_Master'};
                        $sths->finish();
        #               print $slave." ". $lag."\n";
                        if ( $lag > 3 ) {
                                print "$slave is lagging $lag seconds behind. Sleeping 5s...\n";
                                sleep 5;
                                check_slave_lag();
                        }
                        $dbhs->disconnect  or warn $dbhs->errstr;
                }
        }
}
open FILE, "<", $sqlfile or die $!;
my $counter = 0;
my $lines = 0;
$lines++ while <FILE>;
seek FILE, 0, 0;
while (<FILE>) {
        $counter++;
        if ( $counter % $lag_check_interval == 0 ) { check_slave_lag(); }
        my $query = $_;
#       print $query;
        print "Progress: ".$counter."/".$lines."\n";
        my $sth = $dbh->prepare($query);
        $sth->execute() or die $DBI::errstr;
}

