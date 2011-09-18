Summary:	Asynchronous JavaScript Engine
Name:		nodejs
Version:	0.4.12
Release:	1
License:	BSD
Group:		Libraries
URL:		http://nodejs.org/
Source0:	http://nodejs.org/dist/node-v%{version}.tar.gz
# Source0-md5:	a6375eaa43db5356bf443e25b828ae16
Patch0:		%{name}-ev-multiplicity.patch
Patch1:		%{name}-soname.patch
BuildRequires:	c-ares-devel
BuildRequires:	c-ares-devel >= 1.7.4
BuildRequires:	gcc >= 5:4.0
BuildRequires:	libeio-devel
BuildRequires:	libev-devel >= 4.0.0
BuildRequires:	libstdc++-devel
BuildRequires:	python
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	v8-devel >= 3.1.5
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
Requires:	%{name} = %{version}-%{release}

%description devel
Development headers for nodejs.

%prep
%setup -q -n node-v%{version}
%patch0 -p1
%patch1 -p1

%build
# build library
CFLAGS="%{rpmcflags}"
CXXFLAGS="%{rpmcxxflags}"
LDFLAGS="%{rpmcflags}"
%if "%{pld_release}" == "ac"
CC="%{__cc}4"
CXX="%{__cxx}4"
%else
CC="%{__cc}"
CXX="%{__cxx}"
%endif
export CFLAGS LDFLAGS CXXFLAGS CC CXX

export PYTHONPATH=tools
%{__python} tools/waf-light configure \
	--shared-v8 \
	--shared-cares \
	--shared-libev \
	--libdir=%{_libdir} \
	--prefix=%{_prefix}

%{__python} tools/waf-light build \
	--product-type='cshlib'

$CC -o build/default/node -Isrc src/node_main.cc -lnode -Lbuild/default

%install
rm -rf $RPM_BUILD_ROOT
export PYTHONPATH=tools
%{__python} tools/waf-light install \
	--product-type=cshlib \
	--destdir=$RPM_BUILD_ROOT

install -p build/default/node $RPM_BUILD_ROOT%{_bindir}/node

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_libdir}/libnode.so.*.*.*
%ghost %{_libdir}/libnode.so.4
%dir %{_libdir}/node
%{_mandir}/man1/node.1*

%files devel
%defattr(644,root,root,755)
%{_libdir}/libnode.so
%{_includedir}/node
%attr(755,root,root) %{_bindir}/node-waf
%dir %{_libdir}/node/wafadmin
%dir %{_libdir}/node/wafadmin/Tools
%{_libdir}/node/wafadmin/*.py
%{_libdir}/node/wafadmin/Tools/*.py
%{_pkgconfigdir}/nodejs.pc
