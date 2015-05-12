#
# Copyright I.T. Dev Ltd 2014
# http://www.itdev.co.uk
#
import json
import os

class ConfigFile():
  """Provides operations to obtain and set the McVirt configuration for a VM"""

  CURRENT_VERSION = 1
  GIT = '/usr/bin/git'

  def __init__(self):
    """Sets member variables and obtains libvirt domain object"""
    raise NotImplementedError

  @staticmethod
  def getConfigPath(vm_name):
    """Provides the path of the VM-spefic configuration file"""
    raise NotImplementedError

  def getConfig(self):
    """Loads the VM configuration from disk and returns the parsed JSON"""
    config_file = open(self.config_file, 'r')
    config = json.loads(config_file.read())
    config_file.close()

    return config

  def updateConfig(self, callback_function, reason=''):
    """Writes a provided configuration back to the configuration file"""
    config = self.getConfig()
    callback_function(config)
    ConfigFile._writeJSON(config, self.config_file)
    self.config = config
    self.gitAdd(reason)

  def getPermissionConfig(self):
    config = self.getConfig()
    return config['permissions']

  @staticmethod
  def _writeJSON(data, file_name):
    """Parses and writes the JSON VM config file"""
    import pwd
    json_data = json.dumps(data, indent = 2, separators = (',', ': '))

    # Open the config file and write to contents
    config_file = open(file_name, 'w')
    config_file.write(json_data)
    config_file.close()

    # Check file permissions, only giving read/write access to libvirt-qemu/root
    os.chmod(file_name, 0600)
    os.chown(file_name, pwd.getpwnam('libvirt-qemu').pw_uid, 0)

  @staticmethod
  def create(self):
    """Creates a basic VM configuration for new VMs"""
    raise NotImplementedError

  def _upgrade(self, mcvirt_instance, config):
    """Updates the configuration file"""
    raise NotImplementedError

  def upgrade(self, mcvirt_instance):
    """Performs an upgrade of the config file"""
    # Check the version of the configuration file
    if (self._getVersion() < self.CURRENT_VERSION):
      def upgradeConfig(config):
        # Perform the configuration sub-class specific upgrade
        # tasks
        self._upgrade(mcvirt_instance, config)
        # Update the version number of the configuration file to
        # the current version
        config['version'] = self.CURRENT_VERSION
      self.updateConfig(upgradeConfig, 'Updated configuration file \'%s\' from version \'%s\' to \'%s\''
                                       (self.getConfig))

  def _getVersion(self):
    """Returns the version number of the configuration file"""
    config = self.getConfig()
    if ('version' in config.keys()):
      return config['version']
    else:
      return 0

  def gitAdd(self, message=''):
    """Commits changes to an added or modified configuration file"""
    from system import System
    from mcvirt import McVirt
    from auth import Auth
    from cluster.cluster import Cluster
    if (self._checkGitRepo()):
      message += "\nUser: %s\nNode: %s" % (Auth.getUsername(), Cluster.getHostname())
      try:
        System.runCommand([self.GIT, 'add', self.config_file], cwd=McVirt.BASE_STORAGE_DIR)
        System.runCommand([self.GIT, 'commit', '-m', message, self.config_file], cwd=McVirt.BASE_STORAGE_DIR)
        System.runCommand([self.GIT, 'push'], raise_exception_on_failure=False, cwd=McVirt.BASE_STORAGE_DIR)
      except:
        pass

  def gitRemove(self, message=''):
    """Removes and commits a configuration file"""
    from system import System
    from mcvirt import McVirt
    from auth import Auth
    from cluster.cluster import Cluster
    if (self._checkGitRepo()):
      message +=  "\nUser: %s\nNode: %s" % (Auth.getUsername(), Cluster.getHostname())
      try:
        System.runCommand([self.GIT, 'rm', '--cached', self.config_file], cwd=McVirt.BASE_STORAGE_DIR)
        System.runCommand([self.GIT, 'commit', '-m', message], cwd=McVirt.BASE_STORAGE_DIR)
        System.runCommand([self.GIT, 'push'], raise_exception_on_failure=False, cwd=McVirt.BASE_STORAGE_DIR)
      except:
        pass

  def _checkGitRepo(self):
    """Clones the configuration repo, if necessary, and updates the repo"""
    from mcvirt import McVirt
    from mcvirt_config import McVirtConfig
    from system import System

    # Only attempt to create a git repository if the git
    # URL has been set in the McVirt configuration
    mcvirt_config = McVirtConfig().getConfig()
    if (mcvirt_config['git']['repo_domain'] == ''):
      return False

    # Attempt to create git object, if it does not already exist
    if (not os.path.isdir(McVirt.BASE_STORAGE_DIR + '/.git')):

      # Initialise git repository
      System.runCommand([self.GIT, 'init'], cwd=McVirt.BASE_STORAGE_DIR)

      # Set git name and email address
      System.runCommand([self.GIT, 'config', '--file=%s' % McVirt.BASE_STORAGE_DIR + '/.git/config',
                         'user.name', mcvirt_config['git']['commit_name']])
      System.runCommand([self.GIT, 'config', '--file=%s' % McVirt.BASE_STORAGE_DIR + '/.git/config',
                         'user.email', mcvirt_config['git']['commit_email']])

      # Create git-credentials store
      System.runCommand([self.GIT, 'config', '--file=%s' % McVirt.BASE_STORAGE_DIR + '/.git/config',
                         'credential.helper', 'store --file /root/.git-credentials'])
      git_credentials = '%s://%s:%s@%s' % (mcvirt_config['git']['repo_protocol'], mcvirt_config['git']['username'],
                                           mcvirt_config['git']['password'], mcvirt_config['git']['repo_domain'])
      fh = open('/root/.git-credentials', 'w')
      fh.write(git_credentials)
      fh.close()

      # Add the git remote
      System.runCommand([self.GIT, 'remote', 'add', 'origin', mcvirt_config['git']['repo_protocol'] + '://'
                                                              + mcvirt_config['git']['repo_domain'] + '/'
                                                              + mcvirt_config['git']['repo_path']],
                        cwd=McVirt.BASE_STORAGE_DIR)

      # Update the repo
      System.runCommand([self.GIT, 'fetch'], cwd=McVirt.BASE_STORAGE_DIR)
      System.runCommand([self.GIT, 'checkout', 'master'], cwd=McVirt.BASE_STORAGE_DIR)
      System.runCommand([self.GIT, 'branch', '--set-upstream-to', 'origin/master', 'master'], cwd=McVirt.BASE_STORAGE_DIR)

      # Perform an initial commit of the configuration file
      self.gitAdd('Initial commit of configuration file.')

    else:
      # Update repository
      System.runCommand([self.GIT, 'pull'], raise_exception_on_failure=True, cwd=McVirt.BASE_STORAGE_DIR)

    return True