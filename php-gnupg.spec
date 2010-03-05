%define modname gnupg
%define dirname %{modname}
%define soname %{modname}.so
%define inifile A50_%{modname}.ini

Summary:	A wrapper around the gpgme library for PHP
Name:		php-%{modname}
Version:	1.3.1
Release:	%mkrel 17
Group:		Development/PHP
License:	BSD
URL:		http://pecl.php.net/package/gnupg/
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tar.bz2
BuildRequires:	php-devel >= 3:5.2.0
BuildRequires:	gpgme-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
This extension provides methods to interact with gnupg.

%prep

%setup -q -n %{modname}-%{version}
[ "../package*.xml" != "/" ] && mv ../package*.xml .

# lib64 fix
perl -pi -e "s|/lib\b|/%{_lib}|g" config.m4

%build
%serverbuild

export CFLAGS="$CFLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"

phpize
%configure2_5x --with-libdir=%{_lib} \
    --with-%{modname}=shared,%{_prefix}

# antibork
perl -pi -e "s|^GNUPG_SHARED_LIBADD = .*|GNUPG_SHARED_LIBADD = -lgpgme|g" Makefile

%make
mv modules/*.so .

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 

install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d

install -m755 %{soname} %{buildroot}%{_libdir}/php/extensions/

cat > %{buildroot}%{_sysconfdir}/php.d/%{inifile} << EOF
extension = %{soname}
EOF

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files 
%defattr(-,root,root)
%doc tests LICENSE README package*.xml
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}
