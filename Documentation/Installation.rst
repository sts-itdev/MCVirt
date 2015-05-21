============
Installation
============


Building the package
====================


* Ensure that 'dpkg' and 'svn' packages are installed on the machine
* Check out the root of the branch/tag/branch of McVirt
* From within the root of the working copy, run [source:/mcvirt/trunk/build.sh]



Install Operating System
========================


* McVirt is currently build to support Ubuntu 14.04 with native version of dependencies.
* When installing the operating system create the following logical volumes:

  * Root - Create a 50GB partition using ext4. This is used for the operating system, McVirt configurations and ISO images
  * SWAP - leave the suggested SWAP volume unaltered



Installing Package
==================

* Puppet is used install the McVirt package and other tools used on the system. To install puppet, please see wiki:Puppet#Installation
* The McVirt package is retrieved from the Ubuntu repository on orion.

Configure Network
=================




Remove default network
----------------------


* By default, libvirt configures a default network, 'default'.
* This should be removed by performing the following:

::

 sudo mcvirt network delete default
    





Creating/Removing Network
-------------------------


* Networks provide bridges between physical interfaces and virtual machines.
* To create a network on the host, as a superuser perform the following:

::
  
 sudo mcvirt network create <Network name> --interface <Physical interface>
    


* Assuming that there are not any VMs connected to a network, they can be removed using:

::
    
 sudo mcvirt network delete <Network name>

Configure McVirt
-----------------

* The first time McVirt is run, it creates a configuration file for itself, found in */var/lib/mcvirt/config.json*.
* Set the volume group for the VMs to be stored in, within the configuration file.