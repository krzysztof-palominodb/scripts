#!/usr/bin/perl -w

use DBI;
use strict;


my $mysql_host = "host";
my $mysql_user = "user";
my $mysql_pass = "pass";
my $mysql_db = "schema";
my $dsn = "DBI:mysql:database=$mysql_db;host=$mysql_host";

my $dbh = DBI->connect($dsn, $mysql_user, $mysql_pass ) or die $DBI::errstr;

my @slaves = ("10.0.0.1", "10.0.0.2", "10.0.0.3");
my $lag = 0;
my $slave = '';
my $sqlfile = $ARGV[0];
my $lag_check_interval = 100;

sub check_slave_lag {

        foreach(@slaves) {
                $slave = $_;
                my $dbhs = DBI->connect("DBI:mysql:database=$mysql_db;host=$slave", $mysql_user, $mysql_pass ) or die $DBI::errstr;

                my $sths = $dbhs->prepare("SHOW SLAVE STATUS");
                $sths->execute() or die $DBI::errstr;

                my $rows = $sths->fetchrow_hashref();
                $lag = $rows->{'Seconds_Behind_Master'};
                $sths->finish();
                print $slave." ". $lag."\n";
                if ( $lag > 0 ) { print "Sleeping 30s..." ; sleep 30 ; check_slave_lag(); }
                $dbhs->disconnect  or warn $dbhs->errstr;
        }
}

print $sqlfile."\n";
open FILE, "<", $sqlfile or die $!;
my $counter = 0;

while (<FILE>) {
	$counter++;
	if ( $counter % $lag_check_interval == 0 ) { check_slave_lag(); }
	my $query = $_;
	print $query;
	my $sth = $dbh->prepare($query);
	#$sth->execute() or die $DBI::errstr;
}
