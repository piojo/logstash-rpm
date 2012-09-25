# do not repack jar files
%define __os_install_post %{nil}
%define __jar_repack %{nil}
# do not build debug packages
%define debug_package %{nil}
%define libdir %{_datarootdir}/java/%{name}

%define plugins_dir %{_datarootdir}/%{name}/plugins

Name:           logstash
Version:        1.1.1
Release:        2%{?dist}
Summary:        Logstash is a tool for managing events and logs.

Group:          System Environment/Daemons
License:        Apache License, Version 2.0
URL:            http://logstash.net
Source0:        http://semicomplete.com/files/%{name}/%{name}-%{version}-monolithic.jar
Source1:        logstash.init
Source2:        logstash.logrotate
Source3:        logstash.sysconfig
Source4:        logstash.wrapper
Source5:        logstash.conf
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       jre

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils

%description
Logstash is a tool for managing events and logs

%prep
true

%build
true

%install
rm -rf $RPM_BUILD_ROOT

%{__mkdir} -p %{buildroot}%{libdir}
%{__install} -m 755 %{SOURCE0} %{buildroot}%{libdir}

%{__mkdir} -p %{buildroot}%{_bindir}
%{__install} -m 755 %{SOURCE4} %{buildroot}%{_bindir}/logstash

# config
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logstash/conf.d
%{__install} -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logstash/conf.d/logstash.conf

# plugins & patterns
%{__mkdir} -p %{buildroot}%{plugins_dir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/patterns

# logs
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/logstash

# sysconfig and init
%{__mkdir} -p %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/logstash
%{__install} -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/logstash

%{__mkdir} -p %{buildroot}%{_localstatedir}/run/logstash
%{__mkdir} -p %{buildroot}%{_localstatedir}/lock/subsys/logstash

%pre
# create logstash group
if ! getent group logstash >/dev/null; then
        groupadd -r logstash
fi

# create ogstash user
if ! getent passwd logstash >/dev/null; then
        useradd -r -g logstash -d %{base_install_dir} \
            -s /sbin/nologin -c "Logstash" logstash
fi

%post
/sbin/chkconfig --add logstash
if [ $1 -eq 2 ]
then
    read pid < %{_localstatedir}/run/logstash/logstash.pid
    if kill -0 "$pid"
    then
        service logstash restart
    fi
fi

%preun
if [ $1 -eq 0 ]; then
  /sbin/service logstash stop >/dev/null 2>&1
  /sbin/chkconfig --del logstash
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/*
%dir %{plugins_dir}
%dir %{_sysconfdir}/patterns
%dir %{libdir}

%{_sysconfdir}/rc.d/init.d/logstash
%{_sysconfdir}/logrotate.d/logstash

%config(noreplace) %{_sysconfdir}/sysconfig/logstash
%config(noreplace) %{_sysconfdir}/logstash/conf.d/logstash.conf

%{libdir}/*
#%doc LICENSE.txt  NOTICE.txt  README.textile
%defattr(-,logstash,logstash,-)
%{_localstatedir}/run/logstash
%dir %{_localstatedir}/log/logstash


%changelog
* Fri May  4 2012 Maksim Horbul <max@gorbul.net> - 1.1.0-1
- Initial package
