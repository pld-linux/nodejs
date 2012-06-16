Summary:	Asynchronous JavaScript Engine
Name:		nodejs
Version:	0.6.19
Release:	1
License:	BSD and MIT and ASL 2.0 and GPLv3
Group:		Development/Languages
URL:		http://www.nodejs.org/
Source0:	http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz
# Source0-md5:	f5669a9717422b811c6bad1cc961b1e5
Patch1:		%{name}-soname.patch
# force node to use /usr/lib/node as the systemwide module directory
Patch2:		%{name}-libpath.patch
# use /usr/lib64/node as an arch-specific module dir when appropriate
Patch3:		%{name}-lib64path.patch
# Fix linking of zlib
Patch4:		%{name}-shared-zlib.patch
Patch5:		uv-fpic.patch
BuildRequires:	c-ares-devel >= 1.7.4
BuildRequires:	gcc >= 5:4.0
BuildRequires:	libeio-devel
BuildRequires:	libev-devel >= 4.0.0
BuildRequires:	libstdc++-devel
BuildRequires:	python >= 1:2.5.2
BuildRequires:	python-jsmin
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	v8-devel >= 3.6
ExclusiveArch:	%{ix86} %{x8664} arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Node.js is a platform built on Chrome's JavaScript runtime for easily
building fast, scalable network applications. Node.js uses an
event-driven, non-blocking I/O model that makes it lightweight and
efficient, perfect for data-intensive real-time applications that run
across distributed devices.

%package devel
Summary:	Development headers for nodejs
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-waf = %{version}-%{release}
Requires:	gcc
Requires:	libstdc++-devel
Requires:	v8-devel

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
%patch4 -p1
%patch5 -p1

# fix #!/usr/bin/env python -> #!/usr/bin/python:
grep -rl 'bin/env python' tools | xargs %{__sed} -i -e '1s,^#!.*python,#!%{__python},'

%build
CFLAGS="%{rpmcflags} -fPIC"
CPPFLAGS="%{rpmcppflags} -fPIC"
CXXFLAGS="%{rpmcxxflags} -fPIC"
LDFLAGS="%{rpmcflags}"
%if "%{pld_release}" == "ac"
CC="%{__cc}4"
CXX="%{__cxx}4"
%else
CC="%{__cc}"
CXX="%{__cxx}"
%endif
export CFLAGS LDFLAGS CXXFLAGS CC CXX LINKFLAGS_UV

# Error: V8 doesn't like ccache. Please set your CC env var to 'gcc'
CC=${CC#ccache }

# NOT autoconf so dont use macro
export PYTHONPATH=tools
./configure \
	--shared-cares \
	--shared-v8 \
	--shared-zlib \
	--without-npm \
	--libdir=%{_libdir} \
	--prefix=%{_prefix}

# build library
%{__make} dynamiclib
%{__make} program

# relink with shared lib
$CC -o out/Release/node src/node_main.cc -Isrc -Ideps/uv/include -lnode -Lout/Release

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

echo '.so man1/node.1' > $RPM_BUILD_ROOT%{_mandir}/man1/nodejs.1

# for compat of fedora derivered scripts (shebangs)
ln -s node $RPM_BUILD_ROOT%{_bindir}/nodejs

# globally installed node modules (noarch)
install -d $RPM_BUILD_ROOT%{_prefix}/lib/node_modules

# default searchpaths
install -d $RPM_BUILD_ROOT{%{_libdir},%{_prefix}/lib}/node

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
prefix=%{_prefix}
libdir=${prefix}/%{_lib}
includedir=${prefix}/include/node

Name: nodejs
Description: Evented I/O for V8 JavaScript.
Version: ${version}
Cflags: -I${includedir}
EOF

%py_ocomp $RPM_BUILD_ROOT%{_libdir}/node/wafadmin
%py_comp $RPM_BUILD_ROOT%{_libdir}/node/wafadmin
# TODO: check it first
#%%py_postclean %{_libdir}/node/wafadmin

# install documentation
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
cp -a doc/api/* $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
rm $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.markdown
rm $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.json

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md AUTHORS ChangeLog LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/nodejs
%attr(755,root,root) %{_libdir}/libnode.so.*.*.*
%ghost %{_libdir}/libnode.so.6
%dir %{_libdir}/node
%dir %{_prefix}/lib/node
%dir %{_prefix}/lib/node_modules
%{_mandir}/man1/node.1*
%{_mandir}/man1/nodejs.1

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
%{_libdir}/node/wafadmin/*.py[co]
%{_libdir}/node/wafadmin/*.py
%{_libdir}/node/wafadmin/Tools/*.py
%{_libdir}/node/wafadmin/Tools/*.py[co]
