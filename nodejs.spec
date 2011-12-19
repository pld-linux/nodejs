Summary:	Asynchronous JavaScript Engine
Name:		nodejs
Version:	0.6.6
Release:	2
License:	BSD
Group:		Libraries
URL:		http://nodejs.org/
Source0:	http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz
# Source0-md5:	43836ebd6e8e9059c4584e3b5ab50009
Patch1:		%{name}-soname.patch
# force node to use /usr/lib/node as the systemwide module directory
Patch2:		%{name}-libpath.patch
# use /usr/lib64/node as an arch-specific module dir when appropriate
Patch3:		%{name}-lib64path.patch
BuildRequires:	c-ares-devel >= 1.7.4
BuildRequires:	gcc >= 5:4.0
BuildRequires:	libeio-devel
BuildRequires:	libev-devel >= 4.0.0
BuildRequires:	libstdc++-devel
BuildRequires:	python >= 1:2.5.2
BuildRequires:	python-jsmin
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	v8-devel >= 3.6
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

%package doc
Summary:	Evented I/O for V8 JavaScript - documentation
Group:		Documentation

%description doc
Node.js is a server-side JavaScript environment that uses an
asynchronous event-driven model. Node's goal is to provide an easy way
to build scalable network programs.

This package contains the documentation for nodejs.

%package waf
Summary:	Evented I/O for V8 JavaScript - customized WAF build system
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description waf
Node.js is a server-side JavaScript environment that uses an
asynchronous event-driven model. Node's goal is to provide an easy way
to build scalable network programs.

This package contains the customized version of the WAF build system
used by Node.js and many of its modules.

%prep
%setup -q -n node-v%{version}
%patch1 -p1
%if %{_lib} == "lib64"
%patch3 -p1
%else
%patch2 -p1
%endif

%build
%undefine	with_ccache
# build library
CFLAGS="%{rpmcflags} -fPIC"
CXXFLAGS="%{rpmcxxflags} -fPIC"
LDFLAGS="%{rpmcflags}"
%if "%{pld_release}" == "ac"
CC="%{__cc}4"
CXX="%{__cxx}4"
%else
CC="%{__cc}"
CXX="%{__cxx}"
%endif
export CFLAGS LDFLAGS CXXFLAGS CC CXX

# NOT autoconf so dont use macro
export PYTHONPATH=tools
./configure \
	--shared-cares \
	--shared-v8 \
	--shared-zlib \
	--libdir=%{_libdir} \
	--prefix=%{_prefix}

%{__make} dynamiclib
%{__make} program

# relink with shared lib
$CC -o out/Release/node src/node_main.cc -Isrc -Ideps/uv/include -lnode -Lout/Release

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# install shared lib
export PYTHONPATH=tools
%{__python} tools/waf-light install \
	--product-type=cshlib \
	--destdir=$RPM_BUILD_ROOT

chmod a+x $RPM_BUILD_ROOT%{_libdir}/*.so*

# create pkgconfig
install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
cat <<'EOF' > $RPM_BUILD_ROOT%{_pkgconfigdir}/%{name}.pc
version=%{version}
prefix=/usr
libdir=${prefix}/%{_lib}
includedir=${prefix}/include/node

Name: nodejs
Description: Evented I/O for V8 JavaScript.
Version: ${version}
Cflags: -I${includedir}
EOF

# install documentation
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/html
cp -a doc/* $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/html
cd $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
install -d api
mv html/api/*.markdown api
mv html/api/api/* html/api
rm -rf html/api/api
cd -

# remove NPM; it's buggy in 0.6.3
# but really we package npm from separate spec
rm -rf $RPM_BUILD_ROOT%{_libdir}/node_modules
rm $RPM_BUILD_ROOT%{_bindir}/npm

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md AUTHORS ChangeLog LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_libdir}/libnode.so.*.*.*
%ghost %{_libdir}/libnode.so.4
%dir %{_libdir}/node
%{_mandir}/man1/node.1*

%files devel
%defattr(644,root,root,755)
%{_libdir}/libnode.so
%{_includedir}/node
%{_pkgconfigdir}/nodejs.pc

%files doc
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-doc-%{version}

%files waf
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/node-waf
%dir %{_libdir}/node/wafadmin
%dir %{_libdir}/node/wafadmin/Tools
%{_libdir}/node/wafadmin/*.py
%{_libdir}/node/wafadmin/Tools/*.py
