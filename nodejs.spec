# TODO:
# - use system waf

# For the 1.2 branch, we use 0s here
# For 1.3+, we use the three digit versions
%define		somajor 2
%define		sominor 1
%define		sobuild 2
%define		sover %{somajor}.%{sominor}.%{sobuild}

Summary:	Asynchronous JavaScript Engine
Name:		nodejs
Version:	0.1.33
Release:	0
License:	BSD
Group:		Libraries
URL:		http://nodejs.org/
Source0:	http://nodejs.org/dist/node-v%{version}.tar.gz
# Source0-md5:	d34173ead6119b9a593176a9c7522cea
Source1:	http://www.crockford.com/javascript/jsmin.py.txt
# Source1-md5:	0521ddcf3e52457223c6e0d602486a89
BuildRequires:	gcc >= 5:4.0
BuildRequires:	libeio-devel
BuildRequires:	libev-devel >= 3.90
BuildRequires:	libstdc++-devel
BuildRequires:	python
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	udns-devel
BuildRequires:	v8-devel >= 2.1.5
ExclusiveArch:	%{ix86} %{x8664} arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Node's goal is to provide an easy way to build scalable network
programs. In the above example, the two second delay does not prevent
the server from handling new requests. Node tells the operating system
(through epoll, kqueue, /dev/poll, or select) that it should be
notified when the 2 seconds are up or if a new connection is made --
then it goes to sleep. If someone new connects, then it executes the
callback, if the timeout expires, it executes the inner callback. Each
connection is only a small heap allocation.

%package devel
Summary:	Development headers for nodejs
Group:		Development/Libraries

%description devel
Development headers for nodejs.

%prep
%setup -q -n node-v%{version}

%build
# build library

CFLAGS="%{rpmcflags}"
CXXFLAGS="%{rpmcxxflags}"
LDFLAGS="%{rpmcflags}"
%if "%{pld_release}" == "ac"
CC=%{__cc}4
CXX=%{__cxx}4
%else
CC=%{__cc}
CXX=%{__cxx}
%endif
export CFLAGS LDFLAGS CXXFLAGS CC CXX

tools/waf-light configure \
	--system \
	--prefix=%{_prefix}

tools/waf-light build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir},%{_libdir}/node/libraries}

tools/waf-light install \
	--destdir=$RPM_BUILD_ROOT

install lib/*.js $RPM_BUILD_ROOT%{_libdir}/node/libraries/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/node-repl
%dir %{_libdir}/node
%dir %{_libdir}/node/libraries
%{_libdir}/node/libraries/*.js
%{_mandir}/man1/node.1*

%files devel
%defattr(644,root,root,755)
%dir %{_includedir}/node
%{_includedir}/node/*.h
%attr(755,root,root) %{_bindir}/node-waf
%{_libdir}/node/wafadmin/
