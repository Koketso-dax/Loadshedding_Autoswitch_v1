# Define a class to install Node.js and npm packages

class nodejs_setup {
  # Ensure the required packages are installed
  package { 'curl':
    ensure => installed,
  }

  exec { 'download_nodejs':
    command => 'curl -sL https://deb.nodesource.com/setup_18.x | bash -',
    require => Package['curl'],
    creates => '/etc/apt/sources.list.d/nodesource.list',
  }

  package { 'nodejs':
    ensure  => installed,
    require => Exec['download_nodejs'],
  }
}

# Apply the nodejs_setup class to the nodes
node 'web-01.koketsodiale.tech', 'web-02.koketsodiale.tech' {
  include nodejs_setup
}
