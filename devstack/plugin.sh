
gluon_debug() {
    if [ ! -z "$GLUON_DEVSTACK_DEBUG" ] ; then
       "$@" || true # a debug command failing is not a failure
    fi
}

# For debugging purposes, highlight gluon sections
gluon_debug tput setab 1

name=gluon

# All machines using the GLUON mechdriver and server
function pre_install_gluon {
    :
}

function install_gluon {
    cd "$GLUON_DIR"
    echo "Installing $name"
    setup_develop "$GLUON_DIR"
}

function init_gluon {
    :
}

function configure_gluon {
    # TODO(ijw): we need to set up init files here with lines like:
    #iniset /$GLUON_CONF_FILE ml2_gluon enable_vpp_restart $ENABLE_GLUON_RESTART

    # TODO(ijw): likely any config variable listed above should be in settings
    # tODO(ijw): and if it isn't then we need if (set) ; then iniset... ; fi
}


# The Gluon server

server_service_name=gluon-agent

function pre_install_gluon_server {
    :
}

function install_gluon_server {
    :
}

function init_gluon_server {
    # sudo for now, as it needs to connect to GLUON and for that requires root privs
    # to share its shmem comms channel
    run_process $server_service_name "sudo $GLUON_CP_BINARY --config-file /$GlUON_CONF_FILE"
}

function configure_gluon_server {
    :
}

server_do() {
    if is_service_enabled "$server_service_name"; then
       "$@"
    fi
}

if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
    # Set up system services
    echo_summary "Configuring system services $name"
    pre_install_gluon

elif [[ "$1" == "stack" && "$2" == "install" ]]; then
    # Perform installation of service source
    echo_summary "Installing $name"
    install_gluon
    server_do install_gluon_agent

elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    # Configure after the other layer 1 and 2 services have been configured
    echo_summary "Configuring $name"
    configure_gluon

elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
# Initialize and start the service
    echo_summary "Initializing $name"
    init_gluon
fi

if [[ "$1" == "unstack" ]]; then
    # Shut down services
    shut_gluon_down
fi

if [[ "$1" == "clean" ]]; then
    # Remove state and transient data
    # Remember clean.sh first calls unstack.sh
    # no-op
    :
fi
gluon_debug tput setab 9

function neutron_plugin_install_server_packages {
    # TODO(ijw) packages may need installing, like this:
    # install_package bridge-utils
}
