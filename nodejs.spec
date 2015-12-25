#
# Conditional build:
%bcond_without	system_v8	# system v8
%bcond_without	system_uv	# system uv
%bcond_without	shared	# build libnode.so shared library

# NOTES:
# - https://nodejs.org/en/download/releases/

# see "Modules" column in https://nodejs.org/en/download/releases/
%define		node_module_version	11
Summary:	Asynchronous JavaScript Engine
Name:		nodejs
Version:	0.10.40
Release:	3
License:	BSD and MIT and Apache v2.0 and GPL v3
Group:		Development/Languages
Source0:	https://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz
# Source0-md5:	f6ef20f327ecd6cb1586c41c7184290c
Patch1:		%{name}-shared.patch
# force node to use /usr/lib/node as the systemwide module directory
Patch2:		%{name}-libpath.patch
# use /usr/lib64/node as an arch-specific module dir when appropriate
Patch3:		%{name}-lib64path.patch
Patch4:		%{name}-use-system-certs.patch
Patch5:		uv-fpic.patch
# The invalid UTF8 fix has been reverted since this breaks v8 API, which cannot
# be done in a stable distribution release.  This build of nodejs will behave as
# if NODE_INVALID_UTF8 was set.  For more information on the implications, see:
# http://blog.nodejs.org/2014/06/16/openssl-and-breaking-utf-8-change/
Patch6:		%{name}-revert-utf8-v8.patch
Patch7:		%{name}-revert-utf8-node.patch
URL:		https://nodejs.org/
BuildRequires:	c-ares-devel
BuildRequires:	gcc >= 5:4.0
BuildRequires:	http-parser-devel >= 2.0
BuildRequires:	libstdc++-devel
%{?with_system_uv:BuildRequires:	libuv-devel >= 0.10}
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	python >= 1:2.5.2
BuildRequires:	python-jsmin
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	sed >= 4.0
%{?with_system_v8:BuildRequires:	v8-devel >= 3.15.11.18-2}
BuildRequires:	zlib-devel
Requires:	ca-certificates
Provides:	nodejs(engine) = %{version}
Provides:	nodejs(module-version) = %{node_module_version}
Obsoletes:	nodejs-waf
ExclusiveArch:	%{ix86} %{x8664} arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		sover	%(echo %{version} | cut -d. -f2)

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
Requires:	c-ares-devel
Requires:	gcc
Requires:	http-parser-devel
Requires:	libstdc++-devel
%{?with_system_uv:Requires:	libuv-devel}
Requires:	openssl-devel
%{?with_system_v8:Requires:	v8-devel}
Requires:	zlib-devel

%description devel
Development headers for nodejs.

%package doc
Summary:	Evented I/O for V8 JavaScript - documentation
Group:		Documentation
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description doc
Node.js is a server-side JavaScript environment that uses an
asynchronous event-driven model. Node's goal is to provide an easy way
to build scalable network programs.

This package contains the documentation for nodejs.

%prep
%setup -q -n node-v%{version}
%{?with_shared:%patch1 -p1}
%if %{_lib} == "lib64"
%patch3 -p1
%else
%patch2 -p1
%endif
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

grep -r '#!.*env python' -l . | xargs %{__sed} -i -e '1 s,#!.*env python,#!%{__python},'

rm -r deps/npm
rm -r deps/cares
rm -r deps/http_parser
rm -r deps/openssl
%{?with_system_uv:rm -r deps/uv}
%{?with_system_v8:rm -r deps/v8}
rm -r deps/zlib

%build
ver=$(awk '/#define NODE_MODULE_VERSION/{print $NF}' src/node.h)
if [ $ver != %{node_module_version} ]; then
	echo "Set %%define node_module_version to $ver and re-run."
	exit 1
fi

# CC used only to detect if CC is clang, not used for compiling
CC="%{__cc}" \
CXX="%{__cxx}" \
GYP_DEFINES="soname_version=%{sover}" \
./configure \
	%{?with_system_v8:--shared-v8} \
	--shared-zlib \
	--shared-openssl \
	--shared-cares \
	%{?with_system_uv:--shared-libuv} \
	--shared-http-parser \
	--without-npm \
	--without-dtrace \
	--prefix=%{_prefix}

# add LFS defines from libuv (RHBZ#892601)
# CXXFLAGS must be exported, as it is needed for make, not gyp
CXXFLAGS="%{rpmcxxflags} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 -fPIC" \
LDFLAGS="%{rpmldflags}" \
%{__make} -C out V=1 BUILDTYPE=Release

%install
rm -rf $RPM_BUILD_ROOT
%{__python} tools/install.py install "$RPM_BUILD_ROOT" "%{_lib}"

%if %{with shared}
lib=$(basename $RPM_BUILD_ROOT%{_libdir}/libnode.so.*.*.*)
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libnode.so.10
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libnode.so
%endif

echo '.so man1/node.1' > $RPM_BUILD_ROOT%{_mandir}/man1/nodejs.1

install -d $RPM_BUILD_ROOT%{_includedir}/node
cp -p src/*.h $RPM_BUILD_ROOT%{_includedir}/node

# install for node-gyp
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{name}
cp -p common.gypi $RPM_BUILD_ROOT%{_usrsrc}/%{name}
ln -s %{_includedir}/node $RPM_BUILD_ROOT%{_usrsrc}/%{name}/src

# for compat of fedora derivered scripts (shebangs)
ln -s node $RPM_BUILD_ROOT%{_bindir}/nodejs

# globally installed node modules (noarch)
install -d $RPM_BUILD_ROOT%{_prefix}/lib/node_modules

# default searchpaths
install -d $RPM_BUILD_ROOT{%{_libdir},%{_prefix}/lib}/node

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

# install documentation
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
cp -a doc/api/* $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
rm $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.markdown
rm $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.json

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with shared}
%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig
%endif

%files
%defattr(644,root,root,755)
%doc README.md AUTHORS ChangeLog LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/nodejs
%if %{with shared}
%attr(755,root,root) %{_libdir}/libnode.so.*.*.*
%ghost %{_libdir}/libnode.so.10
%endif
%if "%{_lib}" != "lib"
%dir %{_libdir}/node
%endif
%dir %{_prefix}/lib/node
%dir %{_prefix}/lib/node_modules
%{_mandir}/man1/node.1*
%{_mandir}/man1/nodejs.1

%files devel
%defattr(644,root,root,755)
%if %{with shared}
%{_libdir}/libnode.so
%endif
%{_includedir}/node
%{_pkgconfigdir}/nodejs.pc
%{_usrsrc}/%{name}

%files doc
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-doc-%{version}
